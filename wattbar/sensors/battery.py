"""Potencia de batería vía WMI.

`root\\wmi` clase `BatteryStatus` expone `ChargeRate` y `DischargeRate` en **milivatios**
(potencia instantánea), más banderas `Charging`/`Discharging`/`PowerOnline`.
`root\\cimv2` `Win32_Battery.EstimatedChargeRemaining` da el porcentaje.

El sensor es tolerante a fallos: si la conexión WMI se cae, devuelve una lectura vacía y
reintenta inicializar en la siguiente llamada.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class BatteryReading:
    watts_in: float = 0.0       # potencia entrando a la batería (carga)
    watts_out: float = 0.0      # potencia saliendo de la batería (consumo real)
    charging: bool = False
    on_battery: bool = False    # corriendo a batería (descargando o sin AC)
    percent: Optional[float] = None
    present: bool = False


class BatterySensor:
    def __init__(self):
        self._wmi = None        # root\wmi  (BatteryStatus)
        self._cim = None        # root\cimv2 (Win32_Battery, para %)
        self._init()

    def _init(self):
        try:
            import pythoncom
            # WMI usa COM; inicializar en el hilo actual (el del QTimer / main).
            pythoncom.CoInitialize()
        except Exception:
            pass
        try:
            import wmi
            self._wmi = wmi.WMI(namespace="root\\wmi")
            self._cim = wmi.WMI()
        except Exception:
            self._wmi = None
            self._cim = None

    def read(self) -> BatteryReading:
        r = BatteryReading()
        if self._wmi is None:
            self._init()
            if self._wmi is None:
                return r
        try:
            stats = self._wmi.BatteryStatus()
            if stats:
                s = stats[0]
                r.present = True
                r.watts_in = float(getattr(s, "ChargeRate", 0) or 0) / 1000.0
                r.watts_out = float(getattr(s, "DischargeRate", 0) or 0) / 1000.0
                r.charging = bool(getattr(s, "Charging", False))
                discharging = bool(getattr(s, "Discharging", False))
                power_online = bool(getattr(s, "PowerOnline", True))
                r.on_battery = discharging or not power_online
        except Exception:
            self._wmi = None  # forzar re-init la próxima vez
        try:
            if self._cim is not None:
                bats = self._cim.Win32_Battery()
                if bats and bats[0].EstimatedChargeRemaining is not None:
                    r.percent = float(bats[0].EstimatedChargeRemaining)
        except Exception:
            self._cim = None
        return r
