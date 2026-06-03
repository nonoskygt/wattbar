"""Arrancar con Windows vía HKCU\\...\\Run (no requiere admin)."""
import os
import sys
import winreg

_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_NAME = "WattBar"


def _launcher_command():
    """Comando que lanza WattBar sin consola (pythonw + run.pyw)."""
    pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(pyw):
        pyw = sys.executable
    # run.pyw está en la raíz del proyecto (dos niveles arriba de este archivo).
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    script = os.path.join(root, "run.pyw")
    return f'"{pyw}" "{script}"'


def is_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as k:
            val, _ = winreg.QueryValueEx(k, _NAME)
            return bool(val)
    except FileNotFoundError:
        return False
    except OSError:
        return False


def enable():
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as k:
        winreg.SetValueEx(k, _NAME, 0, winreg.REG_SZ, _launcher_command())


def disable():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
            winreg.DeleteValue(k, _NAME)
    except FileNotFoundError:
        pass
    except OSError:
        pass
