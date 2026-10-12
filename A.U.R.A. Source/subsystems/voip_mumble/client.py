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
"""A.U.R.A. VOIP (Mumble) Protocol Adapter, part 1: helpers + TLS compat."""

from __future__ import annotations

import collections
import re
import socket
import ssl
import threading
import time
from dataclasses import replace
from typing import Any, Callable

from core.error_handler import AURAErrorCode, log_diagnostic_error, log_soft_failure
from core.lifecycle import VOIP_CONNECT_TIMEOUT_SEC, VOIP_JOIN_MS
from .runtime import ensure_opus_dll_path
from .models import (
    VOIPAccountConfig,
    VOIPChannel,
    VOIPConnectionState,
    VOIPMessageType,
    VOIPTextMessage,
    VOIPUser,
)

_WORKER_JOIN_SEC = VOIP_JOIN_MS / 1000.0
_INBOUND_PCM_MAX_CHUNKS = 256
_SPEAKING_TIMEOUT_SEC = 3.0
_MAX_CHANNEL_SNAPSHOT = 500
_MAX_USER_SNAPSHOT = 1000
_CHANNEL_PATH_SEP_RE = re.compile(r"\s*(?:/|>|›|»)\s*")


def _split_channel_path(path: str) -> list[str]:
    """Split an alliance channel path ("Fleet 1 / Alpha") into segments."""
    if not path:
        return []
    return [seg for seg in _CHANNEL_PATH_SEP_RE.split(path.strip()) if seg]


def build_mumble_ssl_context(
    allow_self_signed: bool = False,
    certfile: str | None = None,
    keyfile: str | None = None,
) -> ssl.SSLContext:
    """Creates a hardened SSLContext enforcing modern TLS 1.2+ encryption.

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
    if certfile:
        try:
            ctx.load_cert_chain(certfile, keyfile)
        except OSError:
            pass
    if allow_self_signed:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
    return ctx


def _bind_compat_mumble(base_cls: type) -> type:
    """Create an A.U.R.A.-patched Mumble subclass with modern TLS connect."""
    from pymumble_py3 import mumble_pb2 as _pb2

    class AURACompatMumble(base_cls):  # type: ignore[valid-type,misc]
        def connect(self):  # noqa: D102 - verified against pymumble internals
            try:
                server_info = socket.getaddrinfo(self.host, self.port, type=socket.SOCK_STREAM)
                std_sock = socket.socket(server_info[0][0], socket.SOCK_STREAM)
                std_sock.settimeout(10)
            except socket.error:
                self.connected = 3
                return self.connected

            context = build_mumble_ssl_context(
                allow_self_signed=bool(getattr(self, "_aura_allow_self_signed", False)),
                certfile=getattr(self, "certfile", None),
                keyfile=getattr(self, "keyfile", None),
            )
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.options |= (
                ssl.OP_NO_SSLv2
                | ssl.OP_NO_SSLv3
                | ssl.OP_NO_TLSv1
                | ssl.OP_NO_TLSv1_1
            )
            try:
                self.control_socket = context.wrap_socket(std_sock, server_hostname=self.host)
                self.control_socket.connect((self.host, self.port))
                self.control_socket.setblocking(False)

                version = _pb2.Version()
                version.version = (1 << 16) + (2 << 8) + 4
                version.release = self.application
                version.os = "PyMumble A.U.R.A."
                version.os_version = "Python"
                self.send_message(0, version)

                authenticate = _pb2.Authenticate()
                authenticate.username = self.user
                authenticate.password = self.password
                authenticate.tokens.extend(self.tokens)
                authenticate.opus = True
                self.send_message(2, authenticate)
            except (socket.error, ssl.SSLError, OSError):
                self.connected = 3
                return self.connected

            self.connected = 1  # PYMUMBLE_CONN_STATE_AUTHENTICATING
            return self.connected

        def dispatch_control_message(self, msg_type, message):  # noqa: D102
            try:
                if msg_type == 4:  # PYMUMBLE_MSG_TYPES_REJECT
                    mess = _pb2.Reject()
                    mess.ParseFromString(message)
                    self._aura_reject_reason = str(getattr(mess, "reason", "") or "")
            except Exception:
                pass
            return super().dispatch_control_message(msg_type, message)

    AURACompatMumble._aura_reject_reason = ""
    AURACompatMumble._aura_allow_self_signed = False
    return AURACompatMumble


class MumbleProtocolAdapter:
    """Thread-safe voice session wrapper around a pymumble client thread."""

    def __init__(
        self,
        on_state_change: Callable[[VOIPConnectionState, str], None] | None = None,
        on_text_received: Callable[[VOIPTextMessage], None] | None = None,
        on_topology_changed: Callable[[], None] | None = None,
        on_speaking_changed: Callable[[int, str, int, bool], None] | None = None,
    ):
        self.on_state_change = on_state_change
        self.on_text_received = on_text_received
        self.on_topology_changed = on_topology_changed
        self.on_speaking_changed = on_speaking_changed

        self.config: VOIPAccountConfig | None = None
        self.state: VOIPConnectionState = VOIPConnectionState.DISCONNECTED
        self._client: Any | None = None
        self._worker: threading.Thread | None = None
        self._is_running = False
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._bindings: Any | None = None
        self._compat_cls: type | None = None
        self._client_error: str = ""
        self._inbound_pcm: collections.deque = collections.deque(maxlen=_INBOUND_PCM_MAX_CHUNKS)
        self._speaking: dict[int, float] = {}
        self._ptt_active = False
        self._last_topology_sig: tuple = ()

    def _import_pymumble(self):  # noqa: C901
        """Lazy import after Opus DLL registration. Cached on the adapter."""
        if self._bindings is not None:
            return self._bindings
        ensure_opus_dll_path()
        try:
            import pymumble_py3 as bindings  # type: ignore[import-not-found]
            from pymumble_py3 import constants as const  # type: ignore[import-not-found]
        except Exception as exc:
            raise RuntimeError(
                "pymumble is not installed (pip install pymumble) or the native "
                "Opus codec is missing (run tools/fetch_voip_runtime.py)"
            ) from exc
        try:
            bindings.Mumble  # noqa: B018 - attribute probe
        except AttributeError as exc:
            raise RuntimeError("pymumble package exposes no Mumble client class") from exc
        self._bindings = bindings
        self._compat_cls = _bind_compat_mumble(bindings.Mumble)
        self._const = const
        return bindings

    def set_state(self, new_state: VOIPConnectionState, error_msg: str = "") -> None:
        """Updates session state and invokes the listener callback."""
        self.state = new_state
        if error_msg:
            self._client_error = error_msg
        if self.on_state_change:
            try:
                self.on_state_change(new_state, error_msg)
            except Exception as exc:
                log_diagnostic_error(AURAErrorCode.ERR_5001_WORKER_CRASH, exc, "MumbleProtocolAdapter.set_state")

    def connect(self, config: VOIPAccountConfig) -> bool:
        """Starts the async voice session with an ephemeral config copy."""
        if self._worker is not None and self._worker.is_alive():
            self.disconnect()
        if not config.host or not config.username:
            self.set_state(VOIPConnectionState.ERROR, "Host and pilot name are required")
            return False
        try:
            self._import_pymumble()
        except RuntimeError as exc:
            self.set_state(VOIPConnectionState.ERROR, str(exc))
            log_diagnostic_error(AURAErrorCode.ERR_8004_VOIP_AUDIO_DEVICE, exc, "MumbleProtocolAdapter.connect")
            return False
        self.config = replace(config)
        self._client_error = ""
        self._inbound_pcm.clear()
        self._speaking.clear()
        self._stop_event.clear()
        self._is_running = True
        self.set_state(VOIPConnectionState.CONNECTING)
        self._worker = threading.Thread(
            target=self._connection_worker,
            name="AURA_VOIP_Worker",
            daemon=True,
        )
        self._worker.start()
        return True

    def _register_callbacks(self, client: Any) -> None:
        const = self._const
        client.callbacks.set_callback(const.PYMUMBLE_CLBK_CONNECTED, self._cb_connected)
        client.callbacks.set_callback(const.PYMUMBLE_CLBK_DISCONNECTED, self._cb_disconnected)
        client.callbacks.set_callback(const.PYMUMBLE_CLBK_TEXTMESSAGERECEIVED, self._cb_text)
        client.callbacks.set_callback(const.PYMUMBLE_CLBK_SOUNDRECEIVED, self._cb_sound)
        for name in (
            "PYMUMBLE_CLBK_CHANNELCREATED",
            "PYMUMBLE_CLBK_CHANNELUPDATED",
            "PYMUMBLE_CLBK_CHANNELREMOVED",
            "PYMUMBLE_CLBK_USERCREATED",
            "PYMUMBLE_CLBK_USERUPDATED",
            "PYMUMBLE_CLBK_USERREMOVED",
        ):
            try:
                client.callbacks.set_callback(getattr(const, name), self._cb_topology)
            except Exception as exc:
                log_soft_failure(f"MumbleProtocolAdapter._register_callbacks.{name}", exc)

    def _connection_worker(self) -> None:
        """Owns the pymumble thread lifecycle; never runs on the GUI thread."""
        cfg = self.config
        if cfg is None or self._compat_cls is None:
            self.set_state(VOIPConnectionState.ERROR, "VOIP session misconfigured")
            return
        client = None
        try:
            client = self._compat_cls(
                cfg.host.strip(),
                cfg.username.strip(),
                port=int(cfg.port or 64738),
                password=cfg.password,
                tokens=list(cfg.tokens or []),
                reconnect=False,
            )
            client._aura_allow_self_signed = bool(cfg.allow_self_signed_tls)
            client._aura_reject_reason = ""
            self._register_callbacks(client)
            with self._lock:
                self._client = client
            self.set_state(VOIPConnectionState.AUTHENTICATING)
            client.start()
            ready_ok = self._await_ready(client)
            if not self._is_running or self._stop_event.is_set():
                return
            if not ready_ok:
                reason = (getattr(client, "_aura_reject_reason", "") or "").strip()
                self._client_error = reason or "Connection timed out"
                self._classify_failure(reason)
                return
            client.set_receive_sound(True)
            self._auto_join_channel(client, cfg.channel_path)
            self.set_state(VOIPConnectionState.CONNECTED)
            self._pump_audio(client)
        except Exception as exc:
            if self._is_running and not self._stop_event.is_set():
                self._client_error = str(exc) or type(exc).__name__
                self._classify_failure(self._client_error)
            else:
                log_soft_failure("MumbleProtocolAdapter._connection_worker.teardown", exc)
        finally:
            self._teardown_client(client)

    def _await_ready(self, client: Any) -> bool:
        """Poll readiness with a hard timeout; never block indefinitely."""
        deadline = time.monotonic() + VOIP_CONNECT_TIMEOUT_SEC
        while time.monotonic() < deadline:
            if not self._is_running or self._stop_event.is_set():
                return False
            try:
                locked = client.ready_lock.locked()
            except Exception:
                locked = True
            if not locked:
                return True
            reject = str(getattr(client, "_aura_reject_reason", "") or "")
            if reject or getattr(client, "connected", 0) == 3:
                return False
            time.sleep(0.1)
        return False

    def _classify_failure(self, reason: str) -> None:
        text = (reason or "").lower()
        if any(k in text for k in ("password", "username", "auth", "reject", "denied", "token")):
            code = AURAErrorCode.ERR_8001_VOIP_AUTH_FAILED
            hint = reason or "Server rejected credentials"
        elif any(k in text for k in ("name or service", "nodename", "getaddrinfo", "timed out", "timeout", "unreachable", "refused", "reset")):
            code = AURAErrorCode.ERR_8002_VOIP_HOST_UNREACHABLE
            hint = reason or "Host unreachable"
        elif any(k in text for k in ("ssl", "tls", "certificate", "handshake", "eof occurred")):
            code = AURAErrorCode.ERR_8003_VOIP_TLS_HANDSHAKE
            hint = reason or "TLS handshake failed"
        else:
            code = AURAErrorCode.ERR_8002_VOIP_HOST_UNREACHABLE
            hint = reason or "Connection failed"
        try:
            log_diagnostic_error(code, RuntimeError(hint), "MumbleProtocolAdapter._connection_worker")
        except Exception:
            pass
        self.set_state(VOIPConnectionState.ERROR, hint)

    def _pump_audio(self, client: Any) -> None:
        """Keeps the worker alive; drains per-user queues into the PCM deque."""
        while self._is_running and not self._stop_event.is_set():
            try:
                if getattr(client, "connected", 0) not in (2,):
                    break
                try:
                    users = list(client.users.values())
                except Exception:
                    users = []
                for user in users:
                    try:
                        queue = getattr(user, "sound", None)
                        if queue is None or not queue.is_sound():
                            continue
                        chunk = queue.get_sound()
                        if chunk is None or not getattr(chunk, "pcm", b""):
                            continue
                        session = int(user.get("session", 0) or 0)
                        self._inbound_pcm.append((session, bytes(chunk.pcm)))
                        self._mark_speaking(session, user)
                    except Exception as exc:
                        log_soft_failure("MumbleProtocolAdapter._pump_audio.user", exc)
                self._expire_speaking()
            except Exception as exc:
                log_soft_failure("MumbleProtocolAdapter._pump_audio", exc)
            time.sleep(0.02)

    def _teardown_client(self, client: Any) -> None:
        with self._lock:
            if self._client is client:
                self._client = None
        if client is not None:
            try:
                client.stop()
            except Exception as exc:
                log_soft_failure("MumbleProtocolAdapter._teardown_client.stop", exc)
            try:
                if client.is_alive():
                    client.join(timeout=_WORKER_JOIN_SEC)
            except Exception as exc:
                log_soft_failure("MumbleProtocolAdapter._teardown_client.join", exc)

    def _mark_speaking(self, session: int, user: Any) -> None:
        now = time.monotonic()
        was = session in self._speaking
        self._speaking[session] = now
        if not was and self.on_speaking_changed:
            try:
                name = str(user.get("name", "") or "")
                channel = int(user.get("channel_id", -1) or -1)
                self.on_speaking_changed(session, name, channel, True)
            except Exception as exc:
                log_soft_failure("MumbleProtocolAdapter._mark_speaking", exc)

    def _expire_speaking(self) -> None:
        now = time.monotonic()
        for session in [s for s, t in self._speaking.items() if now - t > _SPEAKING_TIMEOUT_SEC]:
            self._speaking.pop(session, None)
            if self.on_speaking_changed:
                try:
                    self.on_speaking_changed(session, "", -1, False)
                except Exception as exc:
                    log_soft_failure("MumbleProtocolAdapter._expire_speaking", exc)

    def _cb_connected(self) -> None:
        self._emit_topology()

    def _cb_disconnected(self) -> None:
        if self._is_running and not self._stop_event.is_set():
            reason = self._client_error or "Server dropped the connection"
            self._classify_failure(reason)
        else:
            self.set_state(VOIPConnectionState.DISCONNECTED)

    def _cb_topology(self, *args: Any) -> None:
        self._emit_topology()

    def _cb_text(self, message: Any) -> None:
        """Runs on a pymumble-spawned thread; keep it short and guarded."""
        try:
            sender_session = -1
            try:
                sessions = list(getattr(message, "session", []) or [])
                if sessions:
                    sender_session = int(sessions[0])
            except Exception:
                sender_session = -1
            channel_ids = list(getattr(message, "channel_id", []) or [])
            body = str(getattr(message, "message", "") or "")
            if not body:
                return
            sender = ""
            channel_name = ""
            client = self._client
            if client is not None:
                try:
                    if sender_session in client.users:
                        sender = str(client.users[sender_session].get("name", "") or "")
                except Exception:
                    sender = ""
                try:
                    if channel_ids and channel_ids[0] in client.channels:
                        channel_name = str(client.channels[channel_ids[0]].get("name", "") or "")
                except Exception:
                    channel_name = ""
            own_name = (self.config.username if self.config else "").strip()
            voip_msg = VOIPTextMessage(
                sender=sender or "Unknown pilot",
                channel_name=channel_name,
                body=body[:4000],
                msg_type=VOIPMessageType.DIRECT if not channel_ids else VOIPMessageType.CHANNEL,
                is_self=bool(own_name and sender and sender.lower() == own_name.lower()),
            )
            if self.on_text_received:
                self.on_text_received(voip_msg)
        except Exception as exc:
            log_soft_failure("MumbleProtocolAdapter._cb_text", exc)

    def _cb_sound(self, user: Any, chunk: Any) -> None:
        try:
            pcm = getattr(chunk, "pcm", b"") or b""
            if not pcm:
                return
            try:
                session = int(user.get("session", 0) or 0)
            except Exception:
                session = 0
            self._inbound_pcm.append((session, bytes(pcm)))
            self._mark_speaking(session, user)
        except Exception as exc:
            log_soft_failure("MumbleProtocolAdapter._cb_sound", exc)

    def _emit_topology(self) -> None:
        try:
            client = self._client
            if client is None:
                return
            try:
                sig = (len(client.channels), len(client.users))
            except Exception:
                sig = ()
            if sig and sig == self._last_topology_sig:
                return
            self._last_topology_sig = sig
            if self.on_topology_changed:
                self.on_topology_changed()
        except Exception as exc:
            log_soft_failure("MumbleProtocolAdapter._emit_topology", exc)

    def snapshot_topology(self) -> tuple[list[VOIPChannel], list[VOIPUser], int]:
        """Thread-safe snapshot of channels, users, and own session id."""
        client = self._client
        if client is None:
            return [], [], -1
        channels: list[VOIPChannel] = []
        users: list[VOIPUser] = []
        own_session = -1
        try:
            with self._lock:
                raw_channels = list(client.channels.values())[:_MAX_CHANNEL_SNAPSHOT]
                raw_users = list(client.users.values())[:_MAX_USER_SNAPSHOT]
                try:
                    own_session = int(client.users.myself_session or -1)
                except Exception:
                    own_session = -1
            by_id = {int(c.get("channel_id", -1)): c for c in raw_channels}
            for raw in raw_channels:
                cid = int(raw.get("channel_id", -1) or 0)
                parent = int(raw.get("parent", -1) or -1)
                path = self._channel_path(by_id, cid)
                count = sum(1 for u in raw_users if int(u.get("channel_id", -1) or -1) == cid)
                channels.append(VOIPChannel(
                    channel_id=cid,
                    name=str(raw.get("name", "") or ""),
                    path=path,
                    parent_id=parent,
                    description=str(raw.get("description", "") or "")[:500],
                    user_count=count,
                    is_temporary=bool(raw.get("temporary", False)),
                ))
            for raw in raw_users:
                session = int(raw.get("session", 0) or 0)
                users.append(VOIPUser(
                    session_id=session,
                    name=str(raw.get("name", "") or ""),
                    channel_id=int(raw.get("channel_id", 0) or 0),
                    is_muted=bool(raw.get("mute", False)),
                    is_deafened=bool(raw.get("deaf", False)),
                    is_self_muted=bool(raw.get("self_mute", False)),
                    is_self_deafened=bool(raw.get("self_deaf", False)),
                    is_speaking=session in self._speaking,
                    is_self=(session == own_session),
                ))
        except Exception as exc:
            log_soft_failure("MumbleProtocolAdapter.snapshot_topology", exc)
        return channels, users, own_session

    @staticmethod
    def _channel_path(by_id: dict[int, Any], channel_id: int) -> str:
        parts: list[str] = []
        seen: set[int] = set()
        current = channel_id
        while current not in seen and current in by_id and len(parts) < 16:
            seen.add(current)
            node = by_id[current]
            name = str(node.get("name", "") or "")
            if name and current != 0:
                parts.insert(0, name)
            try:
                current = int(node.get("parent", -1) or -1)
            except Exception:
                break
            if current < 0:
                break
        return " / ".join(parts)

    def join_channel_path(self, path: str) -> bool:
        """Move own session into the channel matching the alliance path."""
        segments = _split_channel_path(path)
        if not segments:
            return False
        client = self._client
        if client is None or self.state != VOIPConnectionState.CONNECTED:
            self.set_state(VOIPConnectionState.ERROR, "VOIP client is offline")
            return False
        try:
            target = client.channels.find_by_tree(segments)
        except Exception:
            target = None
        if target is None:
            try:
                target = client.channels.find_by_name(segments[-1])
            except Exception as exc:
                log_soft_failure("MumbleProtocolAdapter.join_channel_path.find", exc)
                target = None
        if target is None:
            self.set_state(VOIPConnectionState.ERROR, f"Channel not found: {path}")
            log_diagnostic_error(
                AURAErrorCode.ERR_8005_VOIP_CHANNEL_JOIN_FAILED,
                RuntimeError(path),
                "MumbleProtocolAdapter.join_channel_path",
            )
            return False
        try:
            target.move_in()
            return True
        except Exception as exc:
            log_diagnostic_error(AURAErrorCode.ERR_8005_VOIP_CHANNEL_JOIN_FAILED, exc, "MumbleProtocolAdapter.join_channel_path")
            self.set_state(VOIPConnectionState.ERROR, f"Channel join failed: {path}")
            return False

    def send_channel_text(self, channel_id: int, body: str) -> bool:
        """Send a text message to a voice channel."""
        text = (body or "").strip()
        if not text:
            return False
        client = self._client
        if client is None or self.state != VOIPConnectionState.CONNECTED:
            return False
        try:
            target = client.channels.get(int(channel_id))
            if target is None:
                return False
            target.send_text_message(text[:4000])
            return True
        except Exception as exc:
            log_soft_failure("MumbleProtocolAdapter.send_channel_text", exc)
            return False

    def set_self_mute(self, muted: bool) -> bool:
        """Toggle own microphone mute flag on the server."""
        client = self._client
        if client is None or self.state != VOIPConnectionState.CONNECTED:
            return False
        try:
            myself = client.users.myself
            if myself is None:
                return False
            if muted:
                myself.mute()
            else:
                myself.unmute()
            return True
        except Exception as exc:
            log_soft_failure("MumbleProtocolAdapter.set_self_mute", exc)
            return False

    def set_self_deafen(self, deafened: bool) -> bool:
        """Toggle own deafen flag on the server."""
        client = self._client
        if client is None or self.state != VOIPConnectionState.CONNECTED:
            return False
        try:
            myself = client.users.myself
            if myself is None:
                return False
            if deafened:
                myself.deafen()
            else:
                myself.undeafen()
            return True
        except Exception as exc:
            log_soft_failure("MumbleProtocolAdapter.set_self_deafen", exc)
            return False

    def set_push_to_talk(self, active: bool) -> None:
        """Gate outbound microphone PCM on push-to-talk state."""
        self._ptt_active = bool(active)

    def push_outbound_pcm(self, pcm: bytes) -> bool:
        """Queue microphone PCM for transmission (48kHz mono s16)."""
        if not pcm or not self._ptt_active:
            return False
        client = self._client
        if client is None or self.state != VOIPConnectionState.CONNECTED:
            return False
        try:
            client.sound_output.add_sound(bytes(pcm))
            return True
        except Exception as exc:
            log_soft_failure("MumbleProtocolAdapter.push_outbound_pcm", exc)
            return False

    def pop_inbound_pcm(self) -> list[tuple[int, bytes]]:
        """Drain queued inbound PCM chunks for the Qt playback layer."""
        chunks: list[tuple[int, bytes]] = []
        try:
            while self._inbound_pcm:
                chunks.append(self._inbound_pcm.popleft())
        except Exception as exc:
            log_soft_failure("MumbleProtocolAdapter.pop_inbound_pcm", exc)
        return chunks

    def _auto_join_channel(self, client: Any, path: str) -> None:
        segments = _split_channel_path(path)
        if not segments:
            return
        try:
            target = client.channels.find_by_tree(segments)
        except Exception:
            target = None
        if target is None:
            try:
                target = client.channels.find_by_name(segments[-1])
            except Exception:
                return
        if target is None:
            return
        try:
            target.move_in()
        except Exception as exc:
            log_soft_failure("MumbleProtocolAdapter._auto_join_channel", exc)

    def _wipe_credentials(self) -> None:
        """Zero the in-memory password and drop the config reference."""
        cfg = self.config
        if cfg is not None:
            cfg.wipe_credentials()
        self.config = None

    def disconnect(self) -> None:
        """Stop the worker, join the pymumble thread, purge credentials."""
        self._is_running = False
        self._stop_event.set()
        if self.state != VOIPConnectionState.DISCONNECTED:
            self.set_state(VOIPConnectionState.DISCONNECTING)
        client = self._client
        if client is not None:
            try:
                client.stop()
            except Exception as exc:
                log_soft_failure("MumbleProtocolAdapter.disconnect.stop", exc)
            try:
                if client.is_alive():
                    client.join(timeout=_WORKER_JOIN_SEC)
            except Exception as exc:
                log_soft_failure("MumbleProtocolAdapter.disconnect.join", exc)
        worker = self._worker
        on_worker = worker is not None and threading.current_thread() is worker
        if worker is not None and worker.is_alive() and not on_worker:
            worker.join(timeout=_WORKER_JOIN_SEC + 1.0)
        if not on_worker:
            self._worker = None
        with self._lock:
            self._client = None
        self._inbound_pcm.clear()
        self._speaking.clear()
        self._wipe_credentials()
        self.set_state(VOIPConnectionState.DISCONNECTED)

    @property
    def last_error(self) -> str:
        """Most recent connection failure detail for UI display."""
        return self._client_error

