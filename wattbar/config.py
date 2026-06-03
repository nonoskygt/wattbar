"""Carga y guardado de configuración en %APPDATA%\\WattBar\\config.json.

La config es un dict plano (fácil de extender/guardar). `load()` mezcla los valores
guardados sobre los DEFAULTS, de modo que claves nuevas aparecen sin romper configs viejas.
"""
import json
import os

APP_NAME = "WattBar"
CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "mode": "floating",            # "floating" | "embedded"
    "pos_x": None,                 # None => auto-posicionar sobre la barra de tareas
    "pos_y": None,
    "font_size": 11,
    "show": {
        "consumo": True,           # consumo total real (W) — necesita LHM
        "watts": True,             # flujo de batería ↓entra / ↑sale
        "cpu": True, "mem": True, "gpu": True,
        "vram": True,              # VRAM usada (GB) — NVML
        "temps": True,             # temperatura CPU (LHM) y GPU (NVML)
        "cpu_w": False, "gpu_w": False,   # watts individuales de CPU/GPU
    },
    "lines": 2,                    # 1 = una línea, 2 = dos líneas
    "hide_on_fullscreen": True,
    "update_ms": 1000,
    "lhm_port": 8085,              # puerto del servidor web de LibreHardwareMonitor
    "consumption_base": 15.0,      # W "del resto" (pantalla/RAM/SSD); se autocalibra a batería
    "colors": {
        "in": "#39d353",           # entra (verde)
        "out": "#ffb000",          # sale (ámbar)
        "pc": "#5ad1ff",           # consumo total (cian brillante)
        "label": "#7de2ff",        # etiquetas (cian)
        "value": "#e6e6e6",        # valores
        "temp": "#ff9d5c",         # temperaturas (naranja)
        "warn": "#ff4d4d",         # resaltado alto uso
        "bg": "#0c0e14",           # fondo opaco
        "bg_alpha": 200,           # (compatibilidad)
        "accent": "#ff3df0",       # magenta (el rayo)
    },
}


def load():
    """Devuelve la config mezclando lo guardado sobre los DEFAULTS."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        data = {}
    return _merge(DEFAULTS, data if isinstance(data, dict) else {})


def save(cfg):
    """Persiste la config (crea el directorio si falta)."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    tmp = CONFIG_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    os.replace(tmp, CONFIG_PATH)


def _merge(base, override):
    """Mezcla recursiva: toma la estructura de `base` y pisa con `override`."""
    out = {}
    for key, default_val in base.items():
        ov = override.get(key)
        if isinstance(default_val, dict):
            out[key] = _merge(default_val, ov if isinstance(ov, dict) else {})
        else:
            out[key] = ov if ov is not None or key in override else default_val
    return out
