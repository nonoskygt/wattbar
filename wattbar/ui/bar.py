"""La tira: QWidget OPACO, sin marco y siempre encima, con el texto en HTML.

Nota técnica: usamos fondo OPACO (no WA_TranslucentBackground). Las ventanas
translúcidas/layered sobre la barra de tareas no refrescan sus píxeles tras
cambiar el contenido (se "congelan" en el primer frame). Una ventana opaca se
repinta normalmente vía WM_PAINT y muestra los datos en vivo de forma confiable.
"""
from PySide6 import QtWidgets, QtCore, QtGui

from .theme import fmt_watts, fmt_pct, is_high, fmt_temp, fmt_vram


class WattBar(QtWidgets.QWidget):
    def __init__(self, cfg):
        super().__init__(
            None,
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.Tool,
        )
        self.cfg = cfg
        self.menu_callback = None     # callback(QPoint global) para el menú (clic derecho)
        self.on_moved = None          # callback() tras arrastrar, para persistir posición
        self._drag_offset = None

        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating, True)

        self._label = QtWidgets.QLabel(self)
        self._label.setTextFormat(QtCore.Qt.RichText)
        self._label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(10, 3, 10, 3)
        lay.addWidget(self._label)

        self.apply_font()
        self.update_data(None)

    def apply_font(self):
        f = QtGui.QFont("Consolas", int(self.cfg.get("font_size", 11)))
        f.setStyleHint(QtGui.QFont.Monospace)
        self._label.setFont(f)
        self.adjustSize()

    # ---- contenido ----
    def update_data(self, snap):
        self._label.setText(self._html(snap))
        self._label.adjustSize()
        self.adjustSize()
        self.update()  # repinta el fondo opaco con el nuevo tamaño

    def _html(self, snap):
        c = self.cfg["colors"]
        show = self.cfg.get("show", {})
        if snap is None:
            return '<span style="color:%s">WattBar</span>' % c["label"]
        parts = []
        if show.get("consumo", True):
            parts.append(self._consumo(snap))
        if show.get("watts", True):
            parts.append(
                '<span style="color:%s">BAT</span> '
                '<span style="color:%s">&#8595;%s</span> '
                '<span style="color:%s">&#8593;%s</span>'
                % (c["label"], c["in"], fmt_watts(snap.watts_in),
                   c["out"], fmt_watts(snap.watts_out))
            )
        if show.get("cpu_w", False):
            parts.append(self._wfield("Pcpu", snap.cpu_watts))
        if show.get("gpu_w", False):
            parts.append(self._wfield("Pgpu", snap.gpu_watts))
        if show.get("cpu", True):
            parts.append(self._metric("CPU", snap.cpu))
        if show.get("mem", True):
            parts.append(self._metric("MEM", snap.mem))
        if show.get("gpu", True):
            parts.append(self._metric("GPU", snap.gpu))
        if show.get("vram", True):
            parts.append(self._vram(snap))
        if show.get("temps", True):
            parts.append(self._temp("CPU", snap.cpu_temp))
            parts.append(self._temp("GPU", snap.gpu_temp))

        sep = '<span style="color:#3a3f4b">&nbsp;&nbsp;</span>'
        if int(self.cfg.get("lines", 2)) >= 2 and len(parts) > 1:
            mid = (len(parts) + 1) // 2
            return sep.join(parts[:mid]) + "<br>" + sep.join(parts[mid:])
        return sep.join(parts)

    def _vram(self, snap):
        c = self.cfg["colors"]
        warn = is_high(snap.vram_pct)
        color = "#ffffff" if warn else c["value"]
        bg = ("background-color:%s;" % c["warn"]) if warn else ""
        return ('<span style="color:%s">VRAM</span> '
                '<span style="%scolor:%s">%s</span>'
                % (c["label"], bg, color, fmt_vram(snap.vram_used_mb)))

    def _temp(self, name, t):
        c = self.cfg["colors"]
        warn = t is not None and t >= 85.0
        color = "#ffffff" if warn else c.get("temp", "#ff9d5c")
        bg = ("background-color:%s;" % c["warn"]) if warn else ""
        return ('<span style="color:%s">%s</span> '
                '<span style="%scolor:%s">%s</span>'
                % (c["label"], name, bg, color, fmt_temp(t)))

    def _consumo(self, snap):
        c = self.cfg["colors"]
        if snap.consumption is None:
            val = "--"
        else:
            prefix = "" if snap.consumption_exact else "~"
            val = prefix + fmt_watts(snap.consumption)
        return ('<span style="color:%s">&#9889;PC</span> '
                '<span style="color:%s">%s</span>' % (c["accent"], c["pc"], val))

    def _wfield(self, name, watts):
        c = self.cfg["colors"]
        return ('<span style="color:%s">%s</span> '
                '<span style="color:%s">%s</span>'
                % (c["label"], name, c["value"], fmt_watts(watts)))

    def _metric(self, name, value):
        c = self.cfg["colors"]
        warn = is_high(value)
        color = "#ffffff" if warn else c["value"]
        bg = ("background-color:%s;" % c["warn"]) if warn else ""
        return (
            '<span style="color:%s">%s</span>'
            '<span style="%scolor:%s">&nbsp;%s&nbsp;</span>'
            % (c["label"], name, bg, color, fmt_pct(value))
        )

    # ---- fondo OPACO (rectángulo oscuro que combina con la barra) ----
    def paintEvent(self, event):
        c = self.cfg["colors"]
        p = QtGui.QPainter(self)
        p.fillRect(self.rect(), QtGui.QColor(c["bg"]))
        p.end()

    # ---- arrastre (solo en modo flotante) y menú ----
    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.RightButton and self.menu_callback:
            self.menu_callback(e.globalPosition().toPoint())
            return
        if e.button() == QtCore.Qt.LeftButton:
            self._drag_offset = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
            e.accept()

    def mouseMoveEvent(self, e):
        if self._drag_offset is not None:
            self.move(e.globalPosition().toPoint() - self._drag_offset)
            e.accept()

    def mouseReleaseEvent(self, e):
        if self._drag_offset is not None:
            self.cfg["pos_x"] = self.x()
            self.cfg["pos_y"] = self.y()
            self._drag_offset = None
            if self.on_moved:
                self.on_moved()
