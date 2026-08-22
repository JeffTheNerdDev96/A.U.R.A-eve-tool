"""Bootstrap Qt6 DLL and plugin paths for venv and frozen PyInstaller installs."""
import os
import sys
import site

_QT_PRELOAD_DLLS = ("Qt6Core.dll", "Qt6Gui.dll", "Qt6Widgets.dll")


def _add_dll_dir(path: str) -> None:
    if path and os.path.isdir(path) and hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(path)
        except OSError:
            pass


def _win_isolate_dll_search(qt_bin: str) -> None:
    """Prefer bundled Qt6 DLLs over copies on user PATH."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        # LOAD_LIBRARY_SEARCH_USER_DIRS | LOAD_LIBRARY_SEARCH_SYSTEM32
        try:
            kernel32.SetDefaultDllDirectories(0x400 | 0x800)
        except OSError:
            pass
        if qt_bin and os.path.isdir(qt_bin):
            try:
                kernel32.SetDllDirectoryW(qt_bin)
            except OSError:
                pass
    except Exception:
        pass


def _sanitize_path_for_qt(qt_bin: str) -> None:
    """Replace polluted user PATH with qt_bin + System32 only (frozen installs)."""
    system_root = os.environ.get("SystemRoot", "C:\\Windows")
    safe_parts = [qt_bin, os.path.join(system_root, "System32")]
    os.environ["PATH"] = os.pathsep.join(safe_parts)


def _preload_qt_dlls(qt_bin: str) -> list[str]:
    """Load bundled Qt6 DLLs by absolute path before PyQt extension import."""
    if sys.platform != "win32" or not qt_bin:
        return []
    errors: list[str] = []
    import ctypes
    for name in _QT_PRELOAD_DLLS:
        path = os.path.join(qt_bin, name)
        if not os.path.isfile(path):
            errors.append(f"{name}: file not found at {path}")
            continue
        try:
            ctypes.WinDLL(path)
        except OSError as exc:
            errors.append(f"{name}: {exc} ({path})")
    return errors


def _apply_qt_dirs(
    qt_bin: str,
    qt_plugins: str,
    qt_platforms: str,
    sanitize_path: bool = False,
) -> list[str]:
    for path in (qt_bin, qt_plugins, qt_platforms):
        _add_dll_dir(path)

    if qt_plugins and os.path.isdir(qt_plugins):
        os.environ["QT_PLUGIN_PATH"] = qt_plugins
        if qt_platforms and os.path.isdir(qt_platforms):
            os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = qt_platforms

    if qt_bin and os.path.isdir(qt_bin):
        _win_isolate_dll_search(qt_bin)
        if sanitize_path:
            _sanitize_path_for_qt(qt_bin)
        else:
            path_env = os.environ.get("PATH", "")
            if qt_bin not in path_env:
                os.environ["PATH"] = qt_bin + os.pathsep + path_env

    return _preload_qt_dlls(qt_bin)


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


def configure_frozen_qt_paths() -> list[str]:
    """Configure Qt6 DLL paths for PyInstaller onefile (_MEIPASS) installs."""
    diagnostics: list[str] = []
    meipass = getattr(sys, "_MEIPASS", None)
    if not meipass:
        diagnostics.append("_MEIPASS not set")
        return diagnostics

    diagnostics.append(f"_MEIPASS={meipass}")
    _add_dll_dir(meipass)

    qt_root = os.path.join(meipass, "PyQt6", "Qt6")
    qt_bin = os.path.join(qt_root, "bin")
    qt_plugins = os.path.join(qt_root, "plugins")
    qt_platforms = os.path.join(qt_plugins, "platforms")
    diagnostics.append(f"qt_bin exists={os.path.isdir(qt_bin)} path={qt_bin}")

    if not os.path.isdir(qt_bin):
        diagnostics.append("PyQt6/Qt6/bin missing in frozen bundle")
        return diagnostics

    preload_errors = _apply_qt_dirs(qt_bin, qt_plugins, qt_platforms, sanitize_path=True)
    diagnostics.append(f"PATH={os.environ.get('PATH', '')[:500]}")
    diagnostics.extend(preload_errors)
    return diagnostics


def configure_qt_paths() -> None:
    """Add PyQt6 Qt6 bin/plugins to DLL search path and PATH (venv installs only)."""
    if getattr(sys, "frozen", False):
        configure_frozen_qt_paths()
        return

    qt_bin, qt_plugins, qt_platforms = _find_pyqt6_qt6_dirs()
    if not qt_bin:
        return
    _apply_qt_dirs(qt_bin, qt_plugins, qt_platforms, sanitize_path=False)
