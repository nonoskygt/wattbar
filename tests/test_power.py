"""Tests del lector de potencia LHM (parseo y recorrido del árbol JSON)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from wattbar.sensors.power import _parse_watts, _walk


def test_parse_watts():
    assert _parse_watts("45.2 W") == 45.2
    assert _parse_watts("45,2 W") == 45.2     # coma decimal
    assert _parse_watts("0 W") == 0.0
    assert _parse_watts(None) is None
    assert _parse_watts("n/a") is None


def test_walk_collects_power_and_temperature():
    tree = {
        "Text": "root",
        "Children": [
            {"Text": "CPU", "Children": [
                {"Text": "CPU Package", "Type": "Power",
                 "Value": "45.2 W", "SensorId": "/intelcpu/0/power/0"},
                {"Text": "CPU Package", "Type": "Temperature",
                 "Value": "65 °C", "SensorId": "/intelcpu/0/temperature/0"},
                {"Text": "CPU Core #1", "Type": "Load", "Value": "12 %"},
            ]},
            {"Text": "GPU", "Children": [
                {"Text": "GPU Package", "Type": "Power",
                 "Value": "12.0 W", "SensorId": "/gpu-nvidia/0/power/0"},
            ]},
        ],
    }
    out = []
    _walk(tree, out)
    types = {typ for typ, _s, _t, _v in out}
    names = [t for _typ, _s, t, _v in out]
    assert types == {"Power", "Temperature"}   # 'Load' se ignora
    assert "CPU Package" in names
    assert "GPU Package" in names
