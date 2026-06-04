"""Genera installer/wattbar.ico (rayo magenta sobre fondo oscuro redondeado)."""
import os
from PySide6 import QtWidgets, QtGui, QtCore

app = QtWidgets.QApplication([])
S = 256
pm = QtGui.QPixmap(S, S)
pm.fill(QtCore.Qt.transparent)
p = QtGui.QPainter(pm)
p.setRenderHint(QtGui.QPainter.Antialiasing, True)
p.setPen(QtCore.Qt.NoPen)
# fondo redondeado oscuro
p.setBrush(QtGui.QColor("#0c0e14"))
p.drawRoundedRect(QtCore.QRectF(8, 8, S - 16, S - 16), 48, 48)
# rayo magenta
p.setBrush(QtGui.QColor("#ff3df0"))
pts = [(0.58, 0.12), (0.30, 0.55), (0.50, 0.55), (0.42, 0.88), (0.72, 0.42), (0.52, 0.42)]
p.drawPolygon(QtGui.QPolygonF([QtCore.QPointF(x * S, y * S) for x, y in pts]))
p.end()

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wattbar.ico")
ok = pm.save(out, "ICO")
print("ICO saved:", ok, "->", out)
