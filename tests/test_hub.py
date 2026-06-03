"""Tests de agregación y cálculo de consumo del SensorHub (sensores mockeados)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from wattbar.sensors.hub import SensorHub, Snapshot
from wattbar.sensors.battery import BatteryReading


class _Bat:
    def __init__(self, **kw):
        self.kw = kw

    def read(self):
        return BatteryReading(**self.kw)


class _Sys:
    def read(self):
        return {"cpu": 27.0, "mem": 49.9}


class _Gpu:
    def __init__(self, gw=1.2):
        self.gw = gw

    def read(self):
        return {"gpu": 0.0, "gpu_watts": self.gw}


class _Pow:
    def __init__(self, value):
        self.value = value

    def read(self):
        return self.value


def _hub(bat, gpu, power):
    h = SensorHub.__new__(SensorHub)   # evita inicializar hardware real
    h.cfg = {}
    h._base = 15.0
    h.battery = bat
    h.system = _Sys()
    h.gpu = gpu
    h.power = power
    return h


def test_snapshot_basic_fields():
    h = _hub(_Bat(watts_out=60.4, on_battery=True, present=True, percent=32.0),
             _Gpu(1.2), _Pow(None))
    s = h.read()
    assert isinstance(s, Snapshot)
    assert s.watts_out == 60.4
    assert s.cpu == 27.0 and s.mem == 49.9
    assert s.gpu_watts == 1.2


def test_on_battery_consumption_is_exact_discharge():
    h = _hub(_Bat(watts_out=60.4, on_battery=True, present=True),
             _Gpu(1.2), _Pow({"cpu_watts": 20.0, "gpu_watts": 5.0}))
    s = h.read()
    assert s.consumption == 60.4
    assert s.consumption_exact is True
    assert s.cpu_watts == 20.0


def test_plugged_consumption_is_cpu_plus_gpu_plus_base():
    h = _hub(_Bat(watts_in=70.0, charging=True, on_battery=False, present=True),
             _Gpu(8.0), _Pow({"cpu_watts": 30.0, "gpu_watts": 8.0}))
    s = h.read()
    # 30 (CPU real) + 8 (GPU por NVML) + 15 (base) = 53
    assert abs(s.consumption - 53.0) < 1e-6
    assert s.consumption_exact is False


def test_plugged_without_lhm_has_no_consumption():
    h = _hub(_Bat(watts_in=70.0, charging=True, on_battery=False, present=True),
             _Gpu(8.0), _Pow(None))
    s = h.read()
    assert s.consumption is None
