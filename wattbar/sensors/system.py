"""Uso de CPU y RAM vía psutil."""


class SystemSensor:
    def __init__(self):
        import psutil
        self._psutil = psutil
        # Primera llamada "ceba" el cálculo de %CPU (devuelve 0.0 la primera vez).
        psutil.cpu_percent(interval=None)

    def read(self):
        return {
            "cpu": self._psutil.cpu_percent(interval=None),
            "mem": self._psutil.virtual_memory().percent,
        }
