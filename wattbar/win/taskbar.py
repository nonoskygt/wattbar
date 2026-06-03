"""Posicionado sobre la barra de tareas, detección de pantalla completa y embed.

El embed (modo experimental) hace `SetParent` de la tira dentro de `Shell_TrayWnd`.
En Win11 26200 esto es frágil; `app.py` detecta el fallo y cae a flotante.
"""
import win32api
import win32con
import win32gui
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QPoint

TASKBAR_CLASS = "Shell_TrayWnd"
_RESERVE_RIGHT = 240          # px FÍSICOS libres a la derecha (modo empotrado)
_RESERVE_RIGHT_LOGICAL = 180  # px LÓGICOS libres a la derecha (modo flotante)


def find_taskbar():
    h = win32gui.FindWindow(TASKBAR_CLASS, None)
    return h or None


def taskbar_rect():
    h = find_taskbar()
    if not h:
        return None
    try:
        return win32gui.GetWindowRect(h)  # (l, t, r, b)
    except Exception:
        return None


def _screen_of(widget):
    # Anclar al monitor PRIMARIO (donde vive la barra de tareas), no a donde
    # la ventana caiga por defecto — clave en setups multi-monitor.
    return QGuiApplication.primaryScreen() or widget.screen()


def _clamp(x, y, w, h, g):
    """Mantiene la ventana dentro de la pantalla `g` (geometría lógica de Qt)."""
    x = min(max(int(x), g.left()), g.right() - w)
    y = min(max(int(y), g.top()), g.bottom() - h)
    return int(x), int(y)


def place_floating(widget, cfg):
    """Posiciona la tira sobre la barra de tareas en coordenadas LÓGICAS de Qt.

    QWidget.move() usa píxeles lógicos (independientes de DPI). La franja de la barra
    se deriva de QScreen (no de Win32, que devuelve píxeles físicos); de lo contrario,
    con escalado != 100 % la ventana queda desplazada y se va fuera de pantalla.
    """
    screen = _screen_of(widget)
    # Fijar la ventana a ESTE monitor (evita zona muerta y problemas de DPI mixto).
    wh = widget.windowHandle()
    if wh is not None:
        try:
            wh.setScreen(screen)
        except Exception:
            pass
    g = screen.geometry()
    a = screen.availableGeometry()   # excluye la barra de tareas
    w = widget.width() or 320
    h = widget.height() or 28

    x, y = cfg.get("pos_x"), cfg.get("pos_y")
    if x is not None and y is not None:
        # Respetar el monitor donde está la ventana (multi-monitor): clampar al
        # monitor que contiene su centro, no siempre al primario.
        center = QPoint(int(x) + w // 2, int(y) + h // 2)
        target = QGuiApplication.screenAt(center) or screen
        widget.move(*_clamp(x, y, w, h, target.geometry()))
        return

    # Esquina inferior derecha del área visible (justo arriba de la barra),
    # SIEMPRE dentro del monitor para que no caiga en zona muerta.
    x_pos = a.right() - w - 8
    y_pos = a.bottom() - h - 2
    widget.move(*_clamp(x_pos, y_pos, w, h, a))


def raise_topmost(widget):
    """Re-afirma el z-order por encima de la barra (que también es topmost)."""
    try:
        win32gui.SetWindowPos(
            int(widget.winId()), win32con.HWND_TOPMOST, 0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE,
        )
    except Exception:
        pass


def is_fullscreen_foreground():
    """True si la ventana activa ocupa todo su monitor (juego/video a pantalla completa)."""
    h = win32gui.GetForegroundWindow()
    if not h:
        return False
    try:
        cls = win32gui.GetClassName(h)
    except Exception:
        return False
    if cls in ("Shell_TrayWnd", "WorkerW", "Progman", "Windows.UI.Core.CoreWindow"):
        return False
    try:
        l, t, r, b = win32gui.GetWindowRect(h)
        mon = win32api.MonitorFromWindow(h, win32con.MONITOR_DEFAULTTONEAREST)
        ml, mt, mr, mb = win32api.GetMonitorInfo(mon)["Monitor"]
    except Exception:
        return False
    return l <= ml and t <= mt and r >= mr and b >= mb


def embed(widget):
    """Best-effort: incrusta la tira dentro de la barra de tareas. Devuelve True si pareció funcionar."""
    tb = find_taskbar()
    if not tb:
        return False
    hwnd = int(widget.winId())
    try:
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style = (style | win32con.WS_CHILD) & ~win32con.WS_POPUP
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
        win32gui.SetParent(hwnd, tb)
        l, t, r, b = win32gui.GetWindowRect(tb)
        w = widget.width() or 320
        h = widget.height() or 28
        win32gui.MoveWindow(
            hwnd, (r - l) - w - _RESERVE_RIGHT,
            max(0, ((b - t) - h) // 2), w, h, True,
        )
        return is_embedded(widget)
    except Exception:
        return False


def is_embedded(widget):
    tb = find_taskbar()
    if not tb:
        return False
    try:
        return win32gui.GetParent(int(widget.winId())) == tb
    except Exception:
        return False


def unembed(widget):
    hwnd = int(widget.winId())
    try:
        win32gui.SetParent(hwnd, 0)
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style = (style & ~win32con.WS_CHILD) | win32con.WS_POPUP
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    except Exception:
        pass
