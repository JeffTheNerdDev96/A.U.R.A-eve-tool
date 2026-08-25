# Security & Operational Privacy Policy

## Supported Versions

> [!CAUTION]
> **ALL PREVIOUS ALPHA RELEASES ARE DEPRECATED & UNSUPPORTED**
>
> All earlier development builds and alpha releases — including **v0.1.x**, **v0.2.x**, and **v0.3.x** — are officially **deprecated**. Version **v0.4.0-alpha.1** introduces the Anokis wormhole mapping engine, XMPP tactical communications with ephemeral session security, and full 7-tab UI integration.
>
> **All users and testers must upgrade to v0.4.0-alpha.1 or newer.**

| Version | Supported | Status / Notes | Python Runtime | Architecture |
| :--- | :--- | :--- | :--- | :--- |
| **v0.4.0-alpha.1+** | **Yes** | **Active / Supported** (Anokis, XMPP Chat, Ephemeral Auth, 7-Tab Layout) | Python 3.12+ | 64-bit AMD64 |
| **v0.3.2-alpha.1** | **No** | **Deprecated** (Superseded by v0.4.0) | Python 3.12+ | 64-bit AMD64 |
| **v0.3.1-alpha2** | **No** | **Deprecated** (Superseded by v0.3.2) | Python 3.12+ | 64-bit AMD64 |
| **v0.3.0-alpha1** | **No** | **Deprecated** (Superseded by v0.3.1) | Python 3.12+ | 64-bit AMD64 |
| **v0.2.x** | **No** | **Deprecated** (Superseded due to major architecture overhaul) | Python 3.12+ | 64-bit AMD64 |
| **v0.1.x** | **No** | **Deprecated** (Initial prototype builds) | Legacy Python | 64-bit AMD64 |

---

## Threat Model & Security Posture

A.U.R.A. is engineered with an **offline-first** architecture and **can be used as an offline-only app**. There are no listening server sockets, no remote telemetry beacons, and no cloud AI dependencies. Untrusted input surfaces include:

- Capsuleer chat and paste dialogs (D-Scan, Probe Scanner, EFT fittings)
- EVE Online chat/gamelog files written to disk (third-party player inputs)
- User-selected attachments (images, PDF, DOCX, text)
- Out-of-game XMPP broadcast streams (when explicitly connected by user)
- Crafted content aimed at the local LLM (prompt injection)

### What We Mitigate

| Risk | Mitigation |
|---|---|
| **XMPP Credential Theft / Exposure** | **Zero Disk Persistence:** Passwords, JIDs, and session tokens exist strictly in volatile RAM for the active connection. Never saved to disk, config files, or logs. |
| **XMPP Network Interception** | Mandatory TLS 1.2/1.3 encryption on ports 5222 (STARTTLS) and 5223 (Direct TLS). Configurable certificate verification. |
| **Qt HTML Injection in Chat/XMPP** | `input_safety.escape_html` enforced on all chat, log, and XMPP message renderers. |
| **Rich Clipboard Attacks** | `setAcceptRichText(False)` enforced across all user `QTextEdit` and `QLineEdit` inputs. |
| **Oversized Attachments / Log Spikes** | `config.max_attachment_bytes`, `max_log_read_bytes`, PDF page count, and image pixel caps enforced. |
| **Log Path Traversal / Escape** | `is_safe_log_file` realpath validation under selected Chatlogs/Gamelogs roots. |
| **Model / DLL Planting** | Explicit absolute install-path candidates only; no `cwd` / walk-the-tree `.gguf` fallback. |
| **LLM Prompt Injection** | Delimited `[UNTRUSTED_*]` blocks and strict context length bounds. |

### What We Cannot Fully Prevent

- **Prompt injection** into the local Phi-4 model — mitigated by delimiters and length limits, not cryptographic isolation.
- **Social engineering** via fake intel in EVE chat or fake XMPP broadcast pings — pilots must verify standings and orders before executing fleet actions.

---

## Reporting a Vulnerability

Please report security concerns through the [GitHub Issues](https://github.com/JeffTheNerdDev96/A.U.R.A-eve-tool/issues) page.

For sensitive reports, describe the issue in general terms and request private follow-up.

---

## Manual Verification Checklist

1. Paste `<div>fake alert</div>` in chat or XMPP compose — must render as literal text, not HTML.
2. Attach a file larger than 8 MB — rejected with ingestion error.
3. Establish an XMPP connection, disconnect, and close the app — verify no password or token was written to disk or registry.
4. Custom chatlog folder with symlink outside root — file skipped.
