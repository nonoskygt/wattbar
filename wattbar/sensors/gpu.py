"""GPU NVIDIA vía NVML (pynvml).

Tolera el caso típico de laptop Optimus: si la dGPU está dormida o NVML no está
disponible, devuelve `None` en vez de tirar la app, y reintenta inicializar.
"""


class GpuSensor:
    def __init__(self):
        self._nvml = None
        self._handle = None
        self._init()

    def _init(self):
        try:
            import pynvml
            pynvml.nvmlInit()
            self._handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            self._nvml = pynvml
        except Exception:
            self._nvml = None
            self._handle = None

    def read(self):
        empty = {"gpu": None, "gpu_watts": None, "gpu_temp": None,
                 "vram_used_mb": None, "vram_total_mb": None}
        if self._nvml is None:
            self._init()
            if self._nvml is None:
                return empty
        util = watts = temp = vram_used = vram_total = None
        try:
            util = float(self._nvml.nvmlDeviceGetUtilizationRates(self._handle).gpu)
        except Exception:
            pass
        try:
            watts = self._nvml.nvmlDeviceGetPowerUsage(self._handle) / 1000.0
        except Exception:
            pass
        try:
            temp = float(self._nvml.nvmlDeviceGetTemperature(
                self._handle, self._nvml.NVML_TEMPERATURE_GPU))
        except Exception:
            pass
        try:
            mem = self._nvml.nvmlDeviceGetMemoryInfo(self._handle)
            vram_used = mem.used / 1048576.0
            vram_total = mem.total / 1048576.0
        except Exception:
            pass
        if util is None and watts is None and temp is None and vram_used is None:
            # La dGPU pudo haberse dormido o reiniciado NVML; reintentar luego.
            self._nvml = None
        return {"gpu": util, "gpu_watts": watts, "gpu_temp": temp,
                "vram_used_mb": vram_used, "vram_total_mb": vram_total}
