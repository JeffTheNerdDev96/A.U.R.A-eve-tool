"""Bootstrap Qt6 DLL and plugin paths for venv-based installs (non-frozen)."""
import os
import sys
import site


def _find_pyqt6_qt6_dirs() -> tuple:
    candidates: list[str] = []
    try:
        candidates.extend(site.getsitepackages())
    except Exception:
        pass
    try:
        user_site = site.getusersitepackages()
        if user_site:
            candidates.append(user_site)
    except Exception:
        pass

    app_root = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(app_root, "requirements", "venv", "Lib", "site-packages"))
    candidates.append(os.path.join(app_root, "venv", "Lib", "site-packages"))

    seen: set[str] = set()
    for sp in candidates:
        if not sp:
            continue
        norm = os.path.normcase(os.path.abspath(sp))
        if norm in seen or not os.path.isdir(sp):
            continue
        seen.add(norm)
        qt_root = os.path.join(sp, "PyQt6", "Qt6")
        qt_bin = os.path.join(qt_root, "bin")
        qt_plugins = os.path.join(qt_root, "plugins")
        if os.path.isdir(qt_bin):
            return qt_bin, qt_plugins, os.path.join(qt_plugins, "platforms")

    for sp in candidates:
        if not sp or not os.path.isdir(sp):
            continue
        for root, dirs, _ in os.walk(sp):
            if "PyQt6" in dirs:
                qt_root = os.path.join(root, "PyQt6", "Qt6")
                qt_bin = os.path.join(qt_root, "bin")
                if os.path.isdir(qt_bin):
                    qt_plugins = os.path.join(qt_root, "plugins")
                    return qt_bin, qt_plugins, os.path.join(qt_plugins, "platforms")
            dirs[:] = [d for d in dirs if d != "__pycache__"]

    return None, None, None


def configure_qt_paths() -> None:
    """Add PyQt6 Qt6 bin/plugins to DLL search path and PATH (venv installs only)."""
    if getattr(sys, "frozen", False):
        return

    qt_bin, qt_plugins, qt_platforms = _find_pyqt6_qt6_dirs()
    if not qt_bin:
        return

    for path in (qt_bin, qt_plugins, qt_platforms):
        if path and os.path.isdir(path) and hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(path)
            except OSError:
                pass

    if qt_plugins and os.path.isdir(qt_plugins):
        os.environ["QT_PLUGIN_PATH"] = qt_plugins
        if qt_platforms and os.path.isdir(qt_platforms):
            os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = qt_platforms

    if os.path.isdir(qt_bin):
        path_env = os.environ.get("PATH", "")
        if qt_bin not in path_env:
            os.environ["PATH"] = qt_bin + os.pathsep + path_env
