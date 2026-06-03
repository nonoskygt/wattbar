"""Cableado de la app: QTimer(1s) -> SensorHub.read() -> WattBar.update_data().

Maneja el reposicionado de la tira flotante sobre la barra de tareas (multi-monitor,
re-clampada cada tick) y el ocultado automático cuando hay una app en pantalla completa.
"""
import sys

from PySide6 import QtWidgets, QtCore

from . import config
from .sensors.hub import SensorHub
from .ui.bar import WattBar
from .ui.settings import SettingsDialog
from .win import taskbar
from .win.tray import Tray

import os
import tempfile


class AppContext:
    def __init__(self, app):
        self.app = app
        self.cfg = config.load()
        self.hub = SensorHub(self.cfg)

        self.bar = WattBar(self.cfg)
        self.bar.menu_callback = self._menu_at
        self.bar.on_moved = lambda: config.save(self.cfg)

        self.tray = Tray(self)
        self._hidden_for_fs = False

        self._apply_mode()   # realiza, posiciona y RECIÉN ahí muestra la ventana

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(int(self.cfg.get("update_ms", 1000)))

    # ---------- loop ----------
    def tick(self):
        try:
            self.bar.update_data(self.hub.read())
        except Exception:
            pass
        try:
            self._update_visibility()
            self._keep_positioned()
        except Exception:
            pass

    def _update_visibility(self):
        if not self.cfg.get("hide_on_fullscreen", True):
            if self._hidden_for_fs:
                self.bar.show()
                self._hidden_for_fs = False
            return
        fs = taskbar.is_fullscreen_foreground()
        if fs and not self._hidden_for_fs:
            self.bar.hide()
            self._hidden_for_fs = True
        elif not fs and self._hidden_for_fs:
            self.bar.show()
            self._hidden_for_fs = False

    def _keep_positioned(self):
        if self._hidden_for_fs:
            return
        # Re-posicionar/re-clampar cada tick (salvo durante un arrastre), para que
        # al crecer/encoger (1↔2 líneas) la ventana no se salga del monitor.
        if getattr(self.bar, "_drag_offset", None) is None:
            taskbar.place_floating(self.bar, self.cfg)
        taskbar.raise_topmost(self.bar)

    def _apply_mode(self):
        self.bar.apply_font()
        taskbar.unembed(self.bar)   # realiza la ventana (winId) y asegura top-level
        taskbar.place_floating(self.bar, self.cfg)
        self.bar.show()
        taskbar.raise_topmost(self.bar)

    # ---------- acciones ----------
    def _menu_at(self, global_pos):
        self.tray.contextMenu().popup(global_pos)

    def open_settings(self):
        dlg = SettingsDialog(self.cfg, self._on_settings_applied)
        dlg.exec()

    def _on_settings_applied(self):
        self.timer.setInterval(int(self.cfg.get("update_ms", 1000)))
        self._apply_mode()
        try:
            self.bar.update_data(self.hub.read())
        except Exception:
            pass

    def quit(self):
        self.timer.stop()
        try:
            config.save(self.cfg)   # persistir base autocalibrada y ajustes
        except Exception:
            pass
        taskbar.unembed(self.bar)
        self.app.quit()


_LOCK = None
_CTX = None


def main():
    # Instancia única: si ya hay una corriendo, salir sin crear otra cápsula.
    from PySide6.QtCore import QLockFile
    global _LOCK, _CTX
    _LOCK = QLockFile(os.path.join(tempfile.gettempdir(), "wattbar.lock"))
    _LOCK.setStaleLockTime(0)
    if not _LOCK.tryLock(50):
        return 0

    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)   # vive en la bandeja
    _CTX = AppContext(app)                  # global: mantiene viva la referencia
    return app.exec()
