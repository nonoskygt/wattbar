"""Diálogo de configuración: modo, métricas visibles, fuente, fullscreen y autostart."""
from PySide6 import QtWidgets

from .. import config as cfgmod
from ..win import autostart


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, cfg, on_apply, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.on_apply = on_apply
        self.setWindowTitle("WattBar — Configuración")
        self._build()

    def _build(self):
        form = QtWidgets.QFormLayout(self)

        self.mode = QtWidgets.QComboBox()
        self.mode.addItem("Integrado en la barra (como Traffic Monitor)", "taskbar")
        self.mode.addItem("Flotante (arrastrable, libre)", "floating")
        self.mode.setCurrentIndex(max(0, self.mode.findData(self.cfg.get("mode", "taskbar"))))
        form.addRow("Modo:", self.mode)

        self.lines = QtWidgets.QComboBox()
        self.lines.addItem("1 línea", 1)
        self.lines.addItem("2 líneas", 2)
        self.lines.setCurrentIndex(max(0, self.lines.findData(int(self.cfg.get("lines", 2)))))
        form.addRow("Diseño:", self.lines)

        show = self.cfg.get("show", {})
        self.chk_consumo = QtWidgets.QCheckBox("Consumo total (W) — necesita LibreHardwareMonitor")
        self.chk_consumo.setChecked(show.get("consumo", True))
        self.chk_watts = QtWidgets.QCheckBox("Batería: entra ↓ / sale ↑ (W)")
        self.chk_watts.setChecked(show.get("watts", True))
        self.chk_cpuw = QtWidgets.QCheckBox("Watts de CPU")
        self.chk_cpuw.setChecked(show.get("cpu_w", False))
        self.chk_gpuw = QtWidgets.QCheckBox("Watts de GPU")
        self.chk_gpuw.setChecked(show.get("gpu_w", False))
        self.chk_cpu = QtWidgets.QCheckBox("CPU %"); self.chk_cpu.setChecked(show.get("cpu", True))
        self.chk_mem = QtWidgets.QCheckBox("MEM %"); self.chk_mem.setChecked(show.get("mem", True))
        self.chk_gpu = QtWidgets.QCheckBox("GPU %"); self.chk_gpu.setChecked(show.get("gpu", True))
        self.chk_vram = QtWidgets.QCheckBox("VRAM (GB)"); self.chk_vram.setChecked(show.get("vram", True))
        self.chk_temps = QtWidgets.QCheckBox("Temperaturas CPU / GPU")
        self.chk_temps.setChecked(show.get("temps", True))
        for w in (self.chk_consumo, self.chk_watts, self.chk_cpuw, self.chk_gpuw,
                  self.chk_cpu, self.chk_mem, self.chk_gpu, self.chk_vram, self.chk_temps):
            form.addRow(w)

        self.font = QtWidgets.QSpinBox()
        self.font.setRange(7, 22)
        self.font.setValue(int(self.cfg.get("font_size", 11)))
        form.addRow("Tamaño de fuente:", self.font)

        self.chk_fs = QtWidgets.QCheckBox("Ocultar en pantalla completa")
        self.chk_fs.setChecked(self.cfg.get("hide_on_fullscreen", True))
        form.addRow(self.chk_fs)

        self.chk_auto = QtWidgets.QCheckBox("Iniciar con Windows")
        self.chk_auto.setChecked(autostart.is_enabled())
        form.addRow(self.chk_auto)

        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        btns.accepted.connect(self._accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)

    def _accept(self):
        self.cfg["mode"] = self.mode.currentData()
        self.cfg["lines"] = int(self.lines.currentData())
        self.cfg["show"]["consumo"] = self.chk_consumo.isChecked()
        self.cfg["show"]["vram"] = self.chk_vram.isChecked()
        self.cfg["show"]["temps"] = self.chk_temps.isChecked()
        self.cfg["show"]["watts"] = self.chk_watts.isChecked()
        self.cfg["show"]["cpu_w"] = self.chk_cpuw.isChecked()
        self.cfg["show"]["gpu_w"] = self.chk_gpuw.isChecked()
        self.cfg["show"]["cpu"] = self.chk_cpu.isChecked()
        self.cfg["show"]["mem"] = self.chk_mem.isChecked()
        self.cfg["show"]["gpu"] = self.chk_gpu.isChecked()
        self.cfg["font_size"] = self.font.value()
        self.cfg["hide_on_fullscreen"] = self.chk_fs.isChecked()
        try:
            autostart.enable() if self.chk_auto.isChecked() else autostart.disable()
        except Exception:
            pass
        cfgmod.save(self.cfg)
        if self.on_apply:
            self.on_apply()
        self.accept()
