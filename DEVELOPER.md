# A.U.R.A. Developer Guide

Internal reference for contributors working on the v0.2 codebase.

## Module map

| Module | Purpose |
|--------|---------|
| `app.py` | Entry point: Python version gate, DPI, global excepthook, temp cleanup at startup |
| `ui.py` | Main PyQt6 window, tabs, worker thread, modal analyzers |
| `lifecycle.py` | Ordered shutdown and `cleanup_temp_files()` |
| `engine.py` | LLM inference (`UnifiedInferenceEngine`) and OpenVINO coprocessor mesh |
| `hardware.py` | Device detection and workload routing |
| `error_handler.py` | AURA-ERR codes, `log_diagnostic_error`, HTML error formatting |
| `chat_monitor.py` | EVE chat/gamelog tailer (`LiveChatMonitor` QThread) |
| `location_tracker.py` | Parse current system from Local/Gamelog lines |
| `intel_parser.py` | Single-line intel threat parsing |
| `dscan_parser.py` | D-scan and unified paste parsing |
| `fitting_parser.py` | EFT fit parsing |
| `fitting_stats.py` | Fit resource / EHP calculations |
| `fitting_lab_ui.py` | Fitting Lab tab UI |
| `composition.py` | Fleet vs D-scan role buckets and assessment rules |
| `composition_ui.py` | Composition tab UI |
| `eve_map.py` | Offline stargate graph (`data/eve_map.json`) |
| `map_tab_ui.py` | Map tab pan/zoom UI |
| `eve_data.py` | Ship/module database and tactical grounding |
| `ingestion.py` | Attachments: PDF, DOCX, images, text |
| `threat_alerts.py` | Jump-range threat toasts |
| `theme.py` | Angel Cartel stylesheets and palette |
| `config.py` | Runtime settings singleton |

## Dependency flow

```mermaid
flowchart TD
  app[app.py] --> ui[ui.py]
  ui --> engine[engine.py]
  ui --> chat_monitor[chat_monitor.py]
  ui --> composition_ui[composition_ui.py]
  ui --> fitting_lab[fitting_lab_ui.py]
  ui --> map_tab[map_tab_ui.py]
  chat_monitor --> location_tracker[location_tracker.py]
  chat_monitor --> intel_parser[intel_parser.py]
  composition_ui --> composition[composition.py]
  engine --> hardware[hardware.py]
  engine --> eve_data[eve_data.py]
  ui --> lifecycle[lifecycle.py]
  app --> lifecycle
```

## Error codes

All codes live in `error_handler.py` (`AURAErrorCode` + `ERROR_REGISTRY`). Log output: `A.U.R.A. Source/logs/crash.log` (rotates at 5 MB to `crash.log.old`).

| Series | Domain |
|--------|--------|
| 1xxx | Neural core / model loading |
| 2xxx | Hardware acceleration |
| 3xxx | Parsers and ingestion |
| 4xxx | Chat log monitor / file I/O |
| 5xxx | UI and worker threads |

## Lifecycle

**Startup (`app.py` → `ui.run_app`):**

1. `cleanup_temp_files()` — remove `__pycache__`, stale logs
2. `install_thread_excepthook()` — background thread errors → crash.log
3. `MainWindow` starts `LiveChatMonitor` and idle `QTimer`

**Shutdown (`closeEvent` + `run_app` after `app.exec()`):**

1. `lifecycle.shutdown_application(window)` — stop timer, tray, worker, monitor, unload engine/coprocessor, clear buffers
2. `cleanup_temp_files()` again
3. `sys.exit(ret)`

Coprocessor mesh threads join with up to **500 ms** per thread in `engine.NeuralHardwareCoProcessor.stop_all_workers`.

## Developer checks

From the repo root:

```bat
check_syntax.bat
```

Or manually (Python 3.12+):

```bat
python -m compileall -q -f "A.U.R.A. Source"
```

Launch the app:

```bat
run.bat
```

## Map data

`data/eve_map.json` is bundled with the app (Fuzzwork SDE-derived). There is no in-repo rebuild script; update the JSON externally if the jump graph changes.
