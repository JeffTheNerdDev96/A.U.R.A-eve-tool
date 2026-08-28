# -*- coding: utf-8 -*-
# ==============================================================================
# Adaptive Underworld Recon Array (A.U.R.A.)
# Copyright (C) 2026 JeffTheNerdDev96
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ==============================================================================
"""
A.U.R.A. XMPP Chat Protocol Client & Alliance Broadcast Parser.
Provides asynchronous connection management, RFC 6120/6121 stream negotiation,
STARTTLS / Direct TLS, SASL PLAIN authentication, MUC room interaction (XEP-0045),
and heuristic New Eden fleet broadcast ping extraction.
"""

from __future__ import annotations

import base64
import queue
import re
import socket
import ssl
import threading
import time
import xml.etree.ElementTree as ET
from typing import Callable

from version import VERSION
from core.error_handler import AURAErrorCode, log_diagnostic_error
from core.eve_data import lookup_ship
from .models import (
    XMPPAccountConfig,
    XMPPConnectionState,
    XMPPMessage,
    XMPPMessageType,
    XMPPBroadcastPing,
    XMPPBroadcastPriority,
    XMPPMUCChannel,
    XMPPRosterContact,
)

# Common regex patterns for New Eden alliance broadcast pings
_RE_BROADCAST_HEADER = re.compile(
    r"(?:\*\*\*+\s*(?:ALLIANCE|COALITION|CORP|FLEET)\s*(?:BROADCAST|PING)\s*\*\*\*+|^\s*(?:ALLIANCE|CORP|FLEET)\s*PING:|~~~+\s*(?:This was a\s*)?(?:coord\s*)?broadcast\b)",
    re.IGNORECASE,
)
_RE_CTA = re.compile(r"\b(?:CTA|CALL\s*TO\s*ARMS|MAX\s*NUMBERS|RED\s*ALERT)\b", re.IGNORECASE)
_RE_STRATOP = re.compile(r"\b(?:STRATOP|STRATEGIC(?:\s*OP)?|OBJECTIVE|TIMER|NODE\s*WAR)\b", re.IGNORECASE)
_RE_STAND_DOWN = re.compile(r"\b(?:STAND\s*DOWN|STANDDOWN|CANCELLED|DISPERSE|OP\s*OVER)\b", re.IGNORECASE)
_RE_FORMUP = re.compile(r"\b(?:FORMUP|FORMING|FORM\s*UP|NOW\s*FORMING|IN\s*FLEET|FORUMUP)\b", re.IGNORECASE)

_RE_FC = re.compile(r"(?:FC(?:\s*NAME)?|FLEET\s*COMMANDER(?:\s*NAME)?|COMMANDER)\s*[:\-/]\s*([^\n\r]+)", re.IGNORECASE)
_RE_DOCTRINE = re.compile(r"(?:DOCTRINE|SHIPS?|COMP|BRING)\s*:\s*([^\n\r,]+)", re.IGNORECASE)
_RE_LOCATION = re.compile(
    r"(?:FORMUP(?:\s*LOCATION)?|FORUMUP(?:\s*LOCATION)?|LOC(?:ATION)?|STAGING(?:\s*SYSTEM)?|STAGE|DEST(?:INATION)?|TARGET(?:\s*SYSTEM)?|SYSTEM|MOVE\s*TO)\s*[:\-/]\s*([A-Za-z0-9\- ]+)",
    re.IGNORECASE,
)
_RE_PAP = re.compile(r"(?:PAP(?:\s*TYPE)?|FATIGUE|LINK)\s*:\s*(https?://[^\s]+|[A-Za-z0-9\- ]+)", re.IGNORECASE)
_RE_MUMBLE = re.compile(r"(?:COMMS?|MUMBLE|TS3?|VOICE)\s*:\s*([^\n\r]+)", re.IGNORECASE)


def escape_xml(text: str) -> str:
    """Escapes special XML characters for safe stanza construction."""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def parse_broadcast_ping(raw_body: str) -> XMPPBroadcastPing | None:
    """
    Analyzes message body to determine if it represents a structured EVE alliance broadcast.
    Extracts tactical parameters including FC, doctrine ships, staging system, and urgency.
    """
    if not raw_body or not isinstance(raw_body, str):
        return None

    is_explicit_header = bool(_RE_BROADCAST_HEADER.search(raw_body))
    is_cta = bool(_RE_CTA.search(raw_body))
    is_stratop = bool(_RE_STRATOP.search(raw_body))
    is_standdown = bool(_RE_STAND_DOWN.search(raw_body))
    is_formup = bool(_RE_FORMUP.search(raw_body))

    # If neither explicit header nor tactical keywords match, not an alliance ping
    if not (is_explicit_header or is_cta or is_stratop or is_standdown or is_formup):
        return None

    # Priority determination
    if is_standdown:
        priority = XMPPBroadcastPriority.STAND_DOWN
    elif is_cta:
        priority = XMPPBroadcastPriority.CTA
    elif is_stratop:
        priority = XMPPBroadcastPriority.STRATOP
    elif is_formup:
        priority = XMPPBroadcastPriority.FLEET_FORMUP
    else:
        priority = XMPPBroadcastPriority.INFO

    # Tactical extraction
    fc_name = ""
    fc_m = _RE_FC.search(raw_body)
    if fc_m:
        raw_fc = fc_m.group(1).strip()
        # Clean FC name (strip comments, brackets, or delimiters)
        raw_fc = re.split(r"[|\(\[\n\r]", raw_fc)[0].strip()
        if raw_fc and raw_fc.lower() not in ("unknown", "n/a", "none"):
            fc_name = raw_fc

    staging_system = ""
    loc_m = _RE_LOCATION.search(raw_body)
    if loc_m:
        raw_loc = loc_m.group(1).strip()
        tokens = raw_loc.split()
        if tokens:
            staging_system = tokens[0].strip("(),.").upper()

    doctrine_ships: list[str] = []
    doc_m = _RE_DOCTRINE.search(raw_body)
    if doc_m:
        doc_raw = doc_m.group(1).strip()
        tokens = re.split(r"[/,&+\|]|\band\b", doc_raw)
        for tok in tokens:
            cleaned = tok.strip()
            if cleaned and len(cleaned) >= 3:
                # Validate hull name against SDE database
                ship_data = lookup_ship(cleaned)
                if isinstance(ship_data, dict):
                    doctrine_ships.append(ship_data.get("name") or ship_data.get("canonical_name") or cleaned)
                elif ship_data and hasattr(ship_data, "name"):
                    doctrine_ships.append(ship_data.name)
                else:
                    doctrine_ships.append(cleaned)

    pap_link = ""
    pap_m = _RE_PAP.search(raw_body)
    if pap_m:
        pap_link = pap_m.group(1).strip()

    mumble_channel = ""
    mum_m = _RE_MUMBLE.search(raw_body)
    if mum_m:
        mumble_channel = mum_m.group(1).strip()

    return XMPPBroadcastPing(
        staging_system=staging_system,
        doctrine_ships=doctrine_ships,
        fc_name=fc_name,
        formup_timer="",
        pap_link=pap_link,
        mumble_channel=mumble_channel,
        priority=priority,
        raw_body=raw_body.strip(),
        target_system=staging_system,
    )


class XMPPProtocolAdapter:
    """
    Thread-safe asynchronous network protocol client for XMPP communications.
    Implements RFC 6120 / RFC 6121 / XEP-0045, STARTTLS negotiation, SASL PLAIN auth,
    MUC room joining, Bookmarks discovery (XEP-0048), Roster groups (RFC 6121),
    proactive 12s keepalive, auto-reconnect, and robust XML stream stanza dispatching.
    """

    def __init__(
        self,
        on_state_change: Callable[[XMPPConnectionState, str], None] | None = None,
        on_message_received: Callable[[XMPPMessage], None] | None = None,
        on_room_joined: Callable[[str, str, str], None] | None = None,
        on_roster_updated: Callable[[list[XMPPRosterContact]], None] | None = None,
        on_channel_discovered: Callable[[XMPPMUCChannel], None] | None = None,
        on_directory_discovered: Callable[[list[XMPPMUCChannel]], None] | None = None,
    ):
        self.on_state_change = on_state_change
        self.on_message_received = on_message_received
        self.on_room_joined = on_room_joined
        self.on_roster_updated = on_roster_updated
        self.on_channel_discovered = on_channel_discovered
        self.on_directory_discovered = on_directory_discovered

        self.config: XMPPAccountConfig | None = None
        self.state: XMPPConnectionState = XMPPConnectionState.DISCONNECTED
        self._worker_thread: threading.Thread | None = None
        self._is_running = False
        self._socket: socket.socket | ssl.SSLSocket | None = None
        self._outbound_queue: queue.Queue[str] = queue.Queue()
        self._joined_rooms: set[str] = set()
        self._bound_jid: str = ""
        self._roster: dict[str, XMPPRosterContact] = {}

    def set_state(self, new_state: XMPPConnectionState, error_msg: str = "") -> None:
        """Updates internal connection state and invokes listener callback."""
        self.state = new_state
        if self.on_state_change:
            try:
                self.on_state_change(new_state, error_msg)
            except Exception as exc:
                log_diagnostic_error(AURAErrorCode.ERR_5001_WORKER_CRASH, exc, "XMPPProtocolAdapter.set_state")

    def connect(self, config: XMPPAccountConfig) -> bool:
        """
        Initiates asynchronous connection using the provided in-memory config.
        Credentials are never saved to disk.
        """
        if self.state in (XMPPConnectionState.CONNECTING, XMPPConnectionState.AUTHENTICATING, XMPPConnectionState.CONNECTED):
            self.disconnect()

        self.config = config
        if not config.jid or not config.domain:
            self.set_state(XMPPConnectionState.ERROR, "Invalid JID format (expected user@domain)")
            return False

        self._is_running = True
        self._joined_rooms.clear()
        self._roster.clear()
        self.set_state(XMPPConnectionState.CONNECTING)

        self._worker_thread = threading.Thread(
            target=self._connection_worker,
            name="AURA_XMPP_Worker",
            daemon=True,
        )
        self._worker_thread.start()
        return True

    def disconnect(self) -> None:
        """Terminates active network connection and purges in-memory buffers."""
        self._is_running = False
        self.set_state(XMPPConnectionState.DISCONNECTING)

        # Send closing stream tag if connected
        if self._socket:
            try:
                self._socket.sendall(b"</stream:stream>")
            except Exception:
                pass
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None

        while not self._outbound_queue.empty():
            try:
                self._outbound_queue.get_nowait()
            except queue.Empty:
                break

        self._joined_rooms.clear()
        self._bound_jid = ""
        self._roster.clear()
        self.set_state(XMPPConnectionState.DISCONNECTED)

    def send_message(self, target_jid: str, body: str, is_groupchat: bool = True) -> bool:
        """Sends an outgoing direct or MUC room message over active XMPP stream."""
        if self.state != XMPPConnectionState.CONNECTED or not self.config or not self._is_running:
            return False

        msg_type = "groupchat" if is_groupchat else "chat"
        xml_type = XMPPMessageType.GROUPCHAT if is_groupchat else XMPPMessageType.DIRECT
        ping_data = parse_broadcast_ping(body)
        is_bcast = ping_data is not None

        out_msg = XMPPMessage(
            sender_jid=self._bound_jid or self.config.jid,
            sender_nick=self.config.nickname or self.config.username,
            recipient_jid=target_jid if not is_groupchat else "",
            room_jid=target_jid if is_groupchat else "",
            body=body,
            msg_type=xml_type,
            is_broadcast=is_bcast,
            priority=ping_data.priority if ping_data else XMPPBroadcastPriority.INFO,
            broadcast_ping=ping_data,
            timestamp=time.time(),
        )

        stanza = (
            f"<message to='{escape_xml(target_jid)}' type='{msg_type}'>"
            f"<body>{escape_xml(body)}</body>"
            f"</message>"
        )
        self._outbound_queue.put(stanza)

        if self.on_message_received:
            self.on_message_received(out_msg)
        return True

    def join_room(self, room_jid: str, nickname: str = "") -> bool:
        """Subscribes to an XMPP Multi-User Chat room (XEP-0045)."""
        if not self.config:
            return False

        nick = nickname or self.config.nickname or self.config.username
        self._joined_rooms.add(room_jid)

        if self.state == XMPPConnectionState.CONNECTED and self._is_running:
            stanza = (
                f"<presence to='{escape_xml(room_jid)}/{escape_xml(nick)}'>"
                f"<x xmlns='http://jabber.org/protocol/muc'/>"
                f"</presence>"
            )
            self._outbound_queue.put(stanza)

        if self.on_room_joined:
            self.on_room_joined(room_jid, nick, "Alliance Tactical Room")
        return True

    def leave_room(self, room_jid: str) -> bool:
        """Leaves a joined MUC room."""
        if room_jid in self._joined_rooms:
            self._joined_rooms.remove(room_jid)
            if self.state == XMPPConnectionState.CONNECTED and self._is_running and self.config:
                nick = self.config.nickname or self.config.username
                stanza = f"<presence to='{escape_xml(room_jid)}/{escape_xml(nick)}' type='unavailable'/>"
                self._outbound_queue.put(stanza)
            return True
        return False

    def request_roster(self) -> None:
        """Requests user roster from server (RFC 6121 §2)."""
        if self.state == XMPPConnectionState.CONNECTED and self._is_running:
            self._outbound_queue.put("<iq type='get' id='roster_init'><query xmlns='jabber:iq:roster'/></iq>")

    def request_bookmarks(self) -> None:
        """Requests user bookmarked conference rooms (XEP-0048 Private XML Storage)."""
        if self.state == XMPPConnectionState.CONNECTED and self._is_running:
            self._outbound_queue.put(
                "<iq type='get' id='bm_init'><query xmlns='jabber:iq:private'><storage xmlns='storage:bookmarks'/></query></iq>"
            )

    def request_directory(self, conference_host: str = "") -> None:
        """Queries MUC conference host for public room directory (XEP-0030 disco#items)."""
        if self.state == XMPPConnectionState.CONNECTED and self._is_running and self.config:
            host = conference_host or f"conference.{self.config.domain}"
            self._outbound_queue.put(
                f"<iq to='{escape_xml(host)}' type='get' id='disco_muc'><query xmlns='http://jabber.org/protocol/disco#items'/></iq>"
            )

    def _build_ssl_context(self, allow_self_signed: bool) -> ssl.SSLContext:
        """
        Creates a hardened SSLContext enforcing modern TLS 1.2+ encryption.
        Explicitly disallows deprecated legacy protocols (SSLv2, SSLv3, TLSv1.0, TLSv1.1)
        and weak ciphers to prevent downgrade attacks and satisfy CodeQL security rules.
        """
        ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.options |= (
            ssl.OP_NO_SSLv2
            | ssl.OP_NO_SSLv3
            | ssl.OP_NO_TLSv1
            | ssl.OP_NO_TLSv1_1
            | ssl.OP_CIPHER_SERVER_PREFERENCE
        )
        ctx.set_ciphers(
            "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!eNULL:!MD5:!3DES:!RC4:!DES:!DSS:!SEED:!IDEA"
        )
        if allow_self_signed:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        else:
            ctx.check_hostname = True
            ctx.verify_mode = ssl.CERT_REQUIRED
        return ctx

    def _read_until_tag(self, sock: socket.socket, target_patterns: list[str], timeout: float = 10.0) -> str:
        """Reads raw socket chunks until any target substring pattern is found in the accumulated buffer."""
        sock.settimeout(timeout)
        buffer = ""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    raise ConnectionResetError("Server closed connection during handshake")
                buffer += chunk.decode("utf-8", errors="replace")
                for pat in target_patterns:
                    if pat in buffer:
                        return buffer
            except socket.timeout:
                break
        return buffer

    def _connection_worker(self) -> None:
        """
        Background connection worker.
        Connects via TCP socket, negotiates STARTTLS or Direct TLS, handles SASL authentication,
        binds resource, sends presence, performs discovery, and maintains proactive 12s keepalive loop.
        """
        reconnect_backoff = 1.0

        while self._is_running and self.config:
            cfg = self.config
            host = cfg.host_override.strip() if cfg.host_override.strip() else cfg.domain
            port = cfg.port
            is_direct_tls = (port == 5223) or (cfg.use_tls and port != 5222 and not cfg.host_override)

            try:
                # 1. Establish TCP socket connection
                raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                raw_sock.settimeout(10.0)
                raw_sock.connect((host, port))

                sock: socket.socket | ssl.SSLSocket = raw_sock

                # 2. Direct TLS connection (Port 5223 / Legacy SSL)
                if is_direct_tls:
                    ctx = self._build_ssl_context(cfg.allow_self_signed_tls)
                    server_host = cfg.domain.strip() if cfg.domain else None
                    sock = ctx.wrap_socket(raw_sock, server_hostname=server_host)

                self._socket = sock

                # 3. Stream header exchange
                stream_header = (
                    f"<?xml version='1.0'?>"
                    f"<stream:stream to='{escape_xml(cfg.domain)}' xmlns='jabber:client' "
                    f"xmlns:stream='http://etherx.jabber.org/streams' version='1.0'>"
                )
                sock.sendall(stream_header.encode("utf-8"))

                self._read_until_tag(sock, ["<stream:features", "<features", "<starttls"], timeout=8.0)

                # 4. STARTTLS negotiation (Port 5222 or explicit STARTTLS)
                if cfg.use_tls and not is_direct_tls:
                    sock.sendall(b"<starttls xmlns='urn:ietf:params:xml:ns:xmpp-tls'/>")
                    tls_resp = self._read_until_tag(sock, ["<proceed", "<failure"], timeout=8.0)
                    if "<proceed" not in tls_resp:
                        raise ssl.SSLError(f"Server rejected STARTTLS negotiation: {tls_resp.strip()}")

                    ctx = self._build_ssl_context(cfg.allow_self_signed_tls)
                    server_host = cfg.domain.strip() if cfg.domain else None
                    sock = ctx.wrap_socket(raw_sock, server_hostname=server_host)
                    self._socket = sock

                    # Restart XML stream post-TLS
                    sock.sendall(stream_header.encode("utf-8"))
                    self._read_until_tag(sock, ["<stream:features", "<features"], timeout=8.0)

                # 5. SASL Authentication (PLAIN)
                self.set_state(XMPPConnectionState.AUTHENTICATING)
                auth_raw = f"\0{cfg.username}\0{cfg.password}".encode("utf-8")
                auth_b64 = base64.b64encode(auth_raw).decode("ascii")
                auth_stanza = f"<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl' mechanism='PLAIN'>{auth_b64}</auth>"
                sock.sendall(auth_stanza.encode("utf-8"))

                auth_resp = self._read_until_tag(sock, ["<success", "<failure"], timeout=10.0)
                if "<failure" in auth_resp:
                    raise PermissionError(f"Authentication failed: Invalid credentials for JID '{cfg.jid}'")
                if "<success" not in auth_resp:
                    raise ConnectionError(f"Unexpected SASL response: {auth_resp.strip()}")

                # 6. Stream restart post-authentication
                sock.sendall(stream_header.encode("utf-8"))
                self._read_until_tag(sock, ["<stream:features", "<features"], timeout=8.0)

                # 7. Resource Binding (RFC 6120)
                resource_name = cfg.resource or "AURA-Client"
                bind_stanza = (
                    f"<iq type='set' id='bind_1'>"
                    f"<bind xmlns='urn:ietf:params:xml:ns:xmpp-bind'>"
                    f"<resource>{escape_xml(resource_name)}</resource>"
                    f"</bind></iq>"
                )
                sock.sendall(bind_stanza.encode("utf-8"))
                bind_resp = self._read_until_tag(sock, ["<iq", "id='bind_1'"], timeout=8.0)

                jid_m = re.search(r"<jid>([^<]+)</jid>", bind_resp)
                if jid_m:
                    self._bound_jid = jid_m.group(1).strip()
                else:
                    self._bound_jid = f"{cfg.username}@{cfg.domain}/{resource_name}"

                # 8. Session Establishment
                session_stanza = "<iq type='set' id='sess_1'><session xmlns='urn:ietf:params:xml:ns:xmpp-session'/></iq>"
                try:
                    sock.sendall(session_stanza.encode("utf-8"))
                except Exception:
                    pass

                # 9. Send Initial Presence & Status
                presence_stanza = (
                    "<presence>"
                    "<show>available</show>"
                    "<status>A.U.R.A. Online</status>"
                    "<priority>1</priority>"
                    "</presence>"
                )
                sock.sendall(presence_stanza.encode("utf-8"))

                self.set_state(XMPPConnectionState.CONNECTED)
                reconnect_backoff = 1.0  # Reset backoff on successful session

                # 10. Automatically trigger Roster, Bookmarks, and Directory Discovery
                # 10a. Request Roster
                sock.sendall(b"<iq type='get' id='roster_init'><query xmlns='jabber:iq:roster'/></iq>")
                # 10b. Request Bookmarks (XEP-0048)
                sock.sendall(
                    b"<iq type='get' id='bm_init'><query xmlns='jabber:iq:private'><storage xmlns='storage:bookmarks'/></query></iq>"
                )
                # 10c. Request MUC Directory from conference host
                muc_host = f"conference.{cfg.domain}"
                disco_stanza = f"<iq to='{escape_xml(muc_host)}' type='get' id='disco_muc'><query xmlns='http://jabber.org/protocol/disco#items'/></iq>"
                sock.sendall(disco_stanza.encode("utf-8"))

                # 10d. Auto-join configured rooms and default domain broadcasts
                joined_set = set(cfg.auto_join_rooms)
                domain_bcast = f"broadcasts@{muc_host}"
                joined_set.add(domain_bcast)
                for room in joined_set:
                    self.join_room(room)

                # 11. Main Stanza Processing & Keepalive Loop (12s interval)
                sock.settimeout(0.5)
                recv_buffer = ""
                last_keepalive = time.time()

                while self._is_running:
                    # 11a. Flush outgoing stanzas
                    while not self._outbound_queue.empty():
                        try:
                            out_stanza = self._outbound_queue.get_nowait()
                            sock.sendall(out_stanza.encode("utf-8"))
                        except queue.Empty:
                            break

                    # 11b. Send proactive keepalive ping every 12 seconds
                    if time.time() - last_keepalive > 12.0:
                        try:
                            # Send whitespace heartbeat
                            sock.sendall(b" ")
                            # Send XEP-0199 Ping to domain
                            ping_id = f"aura_ping_{int(time.time())}"
                            ping_stanza = f"<iq type='get' to='{escape_xml(cfg.domain)}' id='{ping_id}'><ping xmlns='urn:xmpp:ping'/></iq>"
                            sock.sendall(ping_stanza.encode("utf-8"))
                            last_keepalive = time.time()
                        except Exception:
                            pass

                    # 11c. Read incoming stream data
                    try:
                        chunk = sock.recv(4096)
                        if not chunk:
                            raise ConnectionResetError("Remote server closed stream.")
                        recv_buffer += chunk.decode("utf-8", errors="replace")
                    except socket.timeout:
                        continue
                    except ssl.SSLError as s_err:
                        if "timed out" in str(s_err).lower():
                            continue
                        raise s_err

                    # 11d. Parse stanzas from buffer
                    recv_buffer = self._process_incoming_stanzas(recv_buffer, sock)

            except PermissionError as perm_err:
                log_diagnostic_error(AURAErrorCode.ERR_7001_XMPP_AUTH_FAILED, perm_err, "XMPPProtocolAdapter._connection_worker")
                self.set_state(XMPPConnectionState.ERROR, str(perm_err))
                break  # Do not auto-reconnect on invalid password
            except (ssl.SSLError, ssl.CertificateError) as ssl_err:
                log_diagnostic_error(AURAErrorCode.ERR_7002_XMPP_TLS_HANDSHAKE, ssl_err, "XMPPProtocolAdapter._connection_worker")
                self.set_state(XMPPConnectionState.ERROR, f"TLS Handshake Error: {ssl_err}")
                break  # Do not auto-reconnect on fatal TLS configuration error
            except (socket.gaierror, socket.timeout, ConnectionRefusedError, ConnectionResetError, OSError) as net_err:
                log_diagnostic_error(AURAErrorCode.ERR_7003_XMPP_HOST_UNREACHABLE, net_err, "XMPPProtocolAdapter._connection_worker")
                if self._is_running and cfg.auto_reconnect:
                    self.set_state(XMPPConnectionState.CONNECTING, f"Connection dropped. Reconnecting in {int(reconnect_backoff)}s...")
                    time.sleep(reconnect_backoff)
                    reconnect_backoff = min(reconnect_backoff * 2.0, 15.0)
                    continue
                else:
                    self.set_state(XMPPConnectionState.ERROR, f"Host unreachable: {net_err}")
                    break
            except Exception as exc:
                log_diagnostic_error(AURAErrorCode.ERR_7001_XMPP_AUTH_FAILED, exc, "XMPPProtocolAdapter._connection_worker")
                if self._is_running and cfg.auto_reconnect:
                    time.sleep(reconnect_backoff)
                    reconnect_backoff = min(reconnect_backoff * 2.0, 15.0)
                    continue
                else:
                    self.set_state(XMPPConnectionState.ERROR, str(exc))
                    break
            finally:
                if self._socket:
                    try:
                        self._socket.close()
                    except Exception:
                        pass
                    self._socket = None

        if self.state not in (XMPPConnectionState.ERROR, XMPPConnectionState.DISCONNECTED):
            self.set_state(XMPPConnectionState.DISCONNECTED)

    def _process_incoming_stanzas(self, buffer: str, sock: socket.socket | ssl.SSLSocket) -> str:
        """
        Extracts and dispatches complete XML stanzas (<message>, <presence>, <iq>) from the stream buffer.
        Returns the remaining unparsed buffer tail.
        """
        pattern = re.compile(r"<(message|presence|iq)\b[^>]*>(?:.*?</\1>|(?<=/>))", re.DOTALL | re.IGNORECASE)

        while True:
            match = pattern.search(buffer)
            if not match:
                single_tag = re.search(r"<(message|presence|iq)\b[^>]*/>", buffer, re.DOTALL | re.IGNORECASE)
                if not single_tag:
                    break
                match = single_tag

            stanza_text = match.group(0)
            buffer = buffer[match.end():]

            try:
                self._dispatch_stanza(stanza_text, sock)
            except Exception as parse_err:
                log_diagnostic_error(AURAErrorCode.ERR_5001_WORKER_CRASH, parse_err, "XMPPProtocolAdapter._process_incoming_stanzas")

        return buffer

    def _dispatch_stanza(self, stanza_text: str, sock: socket.socket | ssl.SSLSocket) -> None:
        """Parses a single validated XML stanza and fires relevant callbacks."""
        try:
            elem = ET.fromstring(stanza_text)
        except Exception:
            return

        tag_name = elem.tag.split("}")[-1].lower() if "}" in elem.tag else elem.tag.lower()

        # ---------------------------------------------------------------------
        # 1. Handle incoming Messages
        # ---------------------------------------------------------------------
        if tag_name == "message":
            from_jid = elem.attrib.get("from", "")
            msg_type_str = elem.attrib.get("type", "chat").lower()
            body_elem = elem.find("{*}body") if elem.find("{*}body") is not None else elem.find("body")

            if body_elem is not None and body_elem.text:
                body_text = body_elem.text.strip()
                is_groupchat = msg_type_str == "groupchat"
                room_jid = from_jid.split("/", 1)[0] if is_groupchat else ""
                sender_nick = from_jid.split("/", 1)[1] if (is_groupchat and "/" in from_jid) else from_jid.split("@", 1)[0]

                # If this is a direct message, dynamically register contact in roster/chats
                if not is_groupchat and from_jid:
                    bare_from = from_jid.split("/", 1)[0]
                    if bare_from not in self._roster:
                        new_contact = XMPPRosterContact(
                            jid=bare_from,
                            name=sender_nick,
                            group="Direct Messages",
                            is_direct_chat=True,
                        )
                        self._roster[bare_from] = new_contact
                        if self.on_roster_updated:
                            self.on_roster_updated(list(self._roster.values()))

                ping_data = parse_broadcast_ping(body_text)
                is_bcast = ping_data is not None

                in_msg = XMPPMessage(
                    sender_jid=from_jid,
                    sender_nick=sender_nick,
                    room_jid=room_jid,
                    body=body_text,
                    msg_type=XMPPMessageType.GROUPCHAT if is_groupchat else XMPPMessageType.DIRECT,
                    is_broadcast=is_bcast,
                    priority=ping_data.priority if ping_data else XMPPBroadcastPriority.INFO,
                    broadcast_ping=ping_data,
                    timestamp=time.time(),
                )

                if self.on_message_received:
                    self.on_message_received(in_msg)

        # ---------------------------------------------------------------------
        # 2. Handle IQ Stanzas (Ping Pong, Version, Roster, Bookmarks, Disco)
        # ---------------------------------------------------------------------
        elif tag_name == "iq":
            iq_type = elem.attrib.get("type", "").lower()
            iq_id = elem.attrib.get("id", "")
            from_jid = elem.attrib.get("from", "")
            to_attr = f" to='{escape_xml(from_jid)}'" if from_jid else ""

            # Check for Ping query (XEP-0199)
            has_ping = any(child.tag.endswith("ping") for child in elem)

            # Check for Version query (XEP-0092)
            has_version = any(child.tag.endswith("query") and "version" in child.tag.lower() for child in elem)
            if not has_version:
                for child in elem:
                    if child.attrib.get("xmlns", "").endswith("iq:version"):
                        has_version = True
                        break

            # Check for Disco Info (XEP-0030)
            has_disco_info = any("disco#info" in child.attrib.get("xmlns", "") for child in elem)

            # A. Inbound IQ "get" requests
            if iq_type == "get":
                if has_ping:
                    # Respond with Pong (omit to attribute if from was omitted by server)
                    pong = f"<iq{to_attr} id='{escape_xml(iq_id)}' type='result'/>"
                    try:
                        sock.sendall(pong.encode("utf-8"))
                    except Exception:
                        pass
                elif has_version:
                    # Respond with Software Version
                    v_resp = (
                        f"<iq{to_attr} id='{escape_xml(iq_id)}' type='result'>"
                        f"<query xmlns='jabber:iq:version'>"
                        f"<name>A.U.R.A.</name><version>{VERSION}</version><os>Windows</os>"
                        f"</query></iq>"
                    )
                    try:
                        sock.sendall(v_resp.encode("utf-8"))
                    except Exception:
                        pass
                elif has_disco_info:
                    # Respond with Disco info
                    disco_resp = (
                        f"<iq{to_attr} id='{escape_xml(iq_id)}' type='result'>"
                        f"<query xmlns='http://jabber.org/protocol/disco#info'>"
                        f"<identity category='client' type='pc' name='A.U.R.A.'/>"
                        f"<feature var='http://jabber.org/protocol/disco#info'/>"
                        f"<feature var='http://jabber.org/protocol/muc'/>"
                        f"<feature var='urn:xmpp:ping'/>"
                        f"<feature var='jabber:iq:version'/>"
                        f"</query></iq>"
                    )
                    try:
                        sock.sendall(disco_resp.encode("utf-8"))
                    except Exception:
                        pass
                elif iq_id:
                    # RFC 6120 §8.2.3: Return feature-not-implemented for unhandled get queries
                    err_resp = (
                        f"<iq{to_attr} id='{escape_xml(iq_id)}' type='error'>"
                        f"<error type='cancel'><feature-not-implemented xmlns='urn:ietf:params:xml:ns:xmpp-stanzas'/></error>"
                        f"</iq>"
                    )
                    try:
                        sock.sendall(err_resp.encode("utf-8"))
                    except Exception:
                        pass

            # B. Inbound IQ "set" requests (e.g. Roster pushes)
            elif iq_type == "set":
                # Check for roster push
                for item in elem.findall(".//{*}item"):
                    item_jid = item.attrib.get("jid", "")
                    item_name = item.attrib.get("name", "") or item_jid.split("@", 1)[0]
                    group_elem = item.find("{*}group")
                    group_name = group_elem.text.strip() if (group_elem is not None and group_elem.text) else "Pilots"
                    if item_jid:
                        self._roster[item_jid] = XMPPRosterContact(
                            jid=item_jid,
                            name=item_name,
                            group=group_name,
                        )
                if self.on_roster_updated and self._roster:
                    self.on_roster_updated(list(self._roster.values()))

                # Acknowledge set
                ack = f"<iq{to_attr} id='{escape_xml(iq_id)}' type='result'/>"
                try:
                    sock.sendall(ack.encode("utf-8"))
                except Exception:
                    pass

            # C. Inbound IQ "result" responses
            elif iq_type == "result":
                # Parse Roster Results (RFC 6121)
                if iq_id == "roster_init" or elem.find(".//{jabber:iq:roster}query") is not None or elem.find(".//{*}item") is not None:
                    for item in elem.findall(".//{*}item"):
                        item_jid = item.attrib.get("jid", "")
                        item_name = item.attrib.get("name", "") or item_jid.split("@", 1)[0]
                        group_elem = item.find("{*}group")
                        group_name = group_elem.text.strip() if (group_elem is not None and group_elem.text) else "Pilots"
                        if item_jid:
                            self._roster[item_jid] = XMPPRosterContact(
                                jid=item_jid,
                                name=item_name,
                                group=group_name,
                            )
                    if self.on_roster_updated and self._roster:
                        self.on_roster_updated(list(self._roster.values()))

                # Parse Bookmarked Conferences (XEP-0048)
                for conf in elem.findall(".//{*}conference"):
                    conf_jid = conf.attrib.get("jid", "")
                    conf_name = conf.attrib.get("name", "") or conf_jid.split("@", 1)[0].replace(".", " ").title()
                    autojoin_val = conf.attrib.get("autojoin", "0").lower()
                    autojoin = autojoin_val in ("1", "true")

                    if conf_jid:
                        chan = XMPPMUCChannel(
                            room_jid=conf_jid,
                            name=conf_name,
                            auto_join=autojoin,
                            is_broadcast_channel="broadcast" in conf_jid.lower(),
                            is_bookmarked=True,
                        )
                        if self.on_channel_discovered:
                            self.on_channel_discovered(chan)
                        if autojoin and conf_jid not in self._joined_rooms:
                            self.join_room(conf_jid)

                # Parse MUC Directory Discovery (XEP-0030 disco#items)
                if iq_id == "disco_muc" or "disco#items" in stanza_text:
                    discovered_rooms: list[XMPPMUCChannel] = []
                    for item in elem.findall(".//{*}item"):
                        room_jid = item.attrib.get("jid", "")
                        room_name = item.attrib.get("name", "") or room_jid.split("@", 1)[0].replace(".", " ").title()
                        if room_jid and "@" in room_jid:
                            r_chan = XMPPMUCChannel(
                                room_jid=room_jid,
                                name=room_name,
                                is_broadcast_channel="broadcast" in room_jid.lower(),
                                is_directory_room=True,
                            )
                            discovered_rooms.append(r_chan)
                    if discovered_rooms and self.on_directory_discovered:
                        self.on_directory_discovered(discovered_rooms)

        # ---------------------------------------------------------------------
        # 3. Handle Presence Updates (MUC joins & Contact Status)
        # ---------------------------------------------------------------------
        elif tag_name == "presence":
            from_jid = elem.attrib.get("from", "")
            pres_type = elem.attrib.get("type", "").lower()
            show_elem = elem.find("{*}show")
            show_val = show_elem.text.strip() if (show_elem is not None and show_elem.text) else "available"
            status_elem = elem.find("{*}status")
            status_val = status_elem.text.strip() if (status_elem is not None and status_elem.text) else ""

            if "/" in from_jid:
                room_or_user, resource_or_nick = from_jid.split("/", 1)
                # Check if this presence is from a joined MUC room
                if room_or_user in self._joined_rooms and pres_type != "error":
                    # XEP-0045: Check if presence corresponds to self-presence (status code 110 or own nick)
                    is_self_presence = False
                    for code_elem in elem.findall(".//{*}status"):
                        if code_elem.attrib.get("code") == "110":
                            is_self_presence = True
                            break

                    my_nick = (self.config.nickname or self.config.username) if self.config else ""
                    if not is_self_presence and my_nick and resource_or_nick.lower() == my_nick.lower():
                        is_self_presence = True

                    if is_self_presence:
                        if pres_type != "unavailable" and self.on_room_joined:
                            self.on_room_joined(room_or_user, resource_or_nick, status_val or "Alliance Channel")
                    else:
                        # Occupant presence update from other pilots in the channel:
                        # Silently ignore to avoid triggering join loop & tree refreshes for hundreds of pilots
                        pass
                else:
                    # Contact presence update for 1:1 pilots / roster
                    bare_user = room_or_user
                    if bare_user in self._roster:
                        self._roster[bare_user].presence_show = "offline" if pres_type == "unavailable" else show_val
                        self._roster[bare_user].presence_status = status_val
                        if self.on_roster_updated:
                            self.on_roster_updated(list(self._roster.values()))

