# Security Policy

## Supported Versions

| Version | Supported | Python Runtime | Architecture |
| :--- | :--- | :--- | :--- |
| **v0.2.0-alpha1+** | **Yes** | Python 3.12+ | 64-bit AMD64 |

## Threat model (local desktop)

A.U.R.A. is an **offline** PyQt6 desktop assistant. There is no network API surface. Untrusted input still arrives from:

- Capsuleer chat and paste dialogs
- EVE Online chat/gamelog files (third-party players)
- User-selected attachments (images, PDF, DOCX, text)
- Crafted content aimed at the local LLM (prompt injection)

### What we mitigate

| Risk | Mitigation |
|------|------------|
| Qt HTML injection in chat | `input_safety.escape_html` on all user-visible chat lines; `format_error_html` escapes dynamic text |
| Rich clipboard paste | `setAcceptRichText(False)` on user `QTextEdit` widgets |
| Oversized attachments / logs | `config.max_attachment_bytes`, `max_log_read_bytes`, PDF/page and image pixel caps |
| Log path escape | `is_safe_log_file` — realpath check under selected Chatlogs/Gamelogs roots |
| Model/DLL planting | Explicit install-path candidates only; no `cwd` / walk-the-tree `.gguf` fallback |
| LLM prompt injection | Delimited `[UNTRUSTED_*]` blocks and context length caps (cannot be fully eliminated) |

### What we cannot fully prevent

- **Prompt injection** into the local Phi-4 model — mitigated by delimiters and length limits, not cryptographic isolation
- **Social engineering** via fake intel in EVE chat — user must treat live intel as untrusted

## Reporting a Vulnerability

Please report security concerns through the [GitHub Issues](https://github.com/JeffTheNerdDev96/A.U.R.A-eve-tool/issues) page.

For sensitive reports, describe the issue in general terms and request private follow-up.

## Manual verification checklist

1. Paste `<div>fake alert</div>` in chat — must render as literal text, not HTML
2. Attach a file larger than 8 MB — rejected with ingestion error
3. `format_error_html` with `custom_msg` containing `<b>` — displays escaped
4. Custom chatlog folder with symlink outside root — file skipped
