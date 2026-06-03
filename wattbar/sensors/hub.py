"""SensorHub: junta batería + sistema + GPU + potencia (LHM) en un Snapshot.

Consumo total:
- A batería => el consumo real EXACTO es la descarga (todo el sistema).
- Enchufado => no es medible por la batería, así que estimamos
  CPU(real, LHM) + GPU(real, NVML/LHM) + base, donde `base` ("el resto":
  pantalla, RAM, SSD, pérdidas) se AUTOCALIBRA cuando estás a batería
  (base = descarga - cpu - gpu). Así el número enchufado es preciso.
"""
from dataclasses import dataclass
from typing import Optional

from .battery import BatterySensor
from .system import SystemSensor
from .gpu import GpuSensor
from .power import LhmPowerSensor


@dataclass
class Snapshot:
    watts_in: float = 0.0
    watts_out: float = 0.0
    charging: bool = False
    on_battery: bool = False
    battery_pct: Optional[float] = None
    cpu: Optional[float] = None
    mem: Optional[float] = None
    gpu: Optional[float] = None
    gpu_watts: Optional[float] = None
    cpu_watts: Optional[float] = None
    cpu_temp: Optional[float] = None        # °C (LHM)
    gpu_temp: Optional[float] = None        # °C (NVML)
    vram_used_mb: Optional[float] = None
    vram_total_mb: Optional[float] = None
    vram_pct: Optional[float] = None
    consumption: Optional[float] = None     # consumo total estimado/real (W)
    consumption_exact: bool = False         # True si viene de la descarga real


class SensorHub:
    def __init__(self, cfg=None):
        self.cfg = cfg if cfg is not None else {}
        self.battery = BatterySensor()
        self.system = SystemSensor()
        self.gpu = GpuSensor()
        self.power = LhmPowerSensor(port=int(self.cfg.get("lhm_port", 8085)))
        self._base = float(self.cfg.get("consumption_base", 15.0))

    def read(self) -> Snapshot:
        b = self.battery.read()
        s = self.system.read()
        g = self.gpu.read()
        p = self.power.read()  # None o {cpu_watts, gpu_watts}

        cpu_w = p.get("cpu_watts") if p else None
        gpu_w = g.get("gpu_watts")
        if gpu_w is None and p:
            gpu_w = p.get("gpu_watts")
        cpu_temp = p.get("cpu_temp") if p else None

        vu = g.get("vram_used_mb")
        vt = g.get("vram_total_mb")
        vram_pct = (vu / vt * 100.0) if (vu is not None and vt) else None

        consumption, exact = self._consumption(b, cpu_w, gpu_w)

        return Snapshot(
            watts_in=b.watts_in,
            watts_out=b.watts_out,
            charging=b.charging,
            on_battery=b.on_battery,
            battery_pct=b.percent,
            cpu=s.get("cpu"),
            mem=s.get("mem"),
            gpu=g.get("gpu"),
            gpu_watts=gpu_w,
            cpu_watts=cpu_w,
            cpu_temp=cpu_temp,
            gpu_temp=g.get("gpu_temp"),
            vram_used_mb=vu,
            vram_total_mb=vt,
            vram_pct=vram_pct,
            consumption=consumption,
            consumption_exact=exact,
        )

    def _consumption(self, b, cpu_w, gpu_w):
        # A batería: la descarga ES el consumo total real.
        if b.on_battery and b.watts_out > 0:
            # Autocalibrar la base "del resto" con la medición real.
            if cpu_w is not None and gpu_w is not None:
                base_now = b.watts_out - cpu_w - gpu_w
                if 2.0 <= base_now <= 80.0:
                    self._base = 0.8 * self._base + 0.2 * base_now
                    self.cfg["consumption_base"] = round(self._base, 1)
            return b.watts_out, True
        # Enchufado: estimar con CPU+GPU reales + base autocalibrada.
        if cpu_w is not None:
            return cpu_w + (gpu_w or 0.0) + self._base, False
        return None, False


if __name__ == "__main__":
    import time
    hub = SensorHub()
    hub.read()
    time.sleep(0.5)
    print(hub.read())
