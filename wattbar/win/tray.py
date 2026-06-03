"""Ícono de bandeja (área de notificación) con menú: Configuración / Salir."""
from PySide6 import QtWidgets, QtGui, QtCore


def make_icon():
    """Genera un ícono de rayo magenta (sin archivo externo)."""
    pm = QtGui.QPixmap(32, 32)
    pm.fill(QtCore.Qt.transparent)
    p = QtGui.QPainter(pm)
    p.setRenderHint(QtGui.QPainter.Antialiasing, True)
    p.setPen(QtCore.Qt.NoPen)
    p.setBrush(QtGui.QColor("#ff3df0"))
    pts = [
        QtCore.QPointF(18, 2), QtCore.QPointF(7, 18), QtCore.QPointF(15, 18),
        QtCore.QPointF(12, 30), QtCore.QPointF(25, 12), QtCore.QPointF(17, 12),
    ]
    p.drawPolygon(QtGui.QPolygonF(pts))
    p.end()
    return QtGui.QIcon(pm)


class Tray(QtWidgets.QSystemTrayIcon):
    def __init__(self, ctx):
        super().__init__(make_icon())
        self.ctx = ctx
        self.setToolTip("WattBar")

        menu = QtWidgets.QMenu()
        menu.addAction("Configuración…").triggered.connect(ctx.open_settings)
        menu.addSeparator()
        menu.addAction("Salir").triggered.connect(ctx.quit)
        self.setContextMenu(menu)

        self.activated.connect(self._on_activated)
        self.show()

    def _on_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:  # clic izquierdo
            self.ctx.open_settings()

    def notify(self, title, msg):
        try:
            self.showMessage(title, msg, self.icon(), 5000)
        except Exception:
            pass
