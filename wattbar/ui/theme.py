"""Helpers de formato (puros, testeables) para los valores de la tira."""
from typing import Optional


def fmt_watts(w: Optional[float]) -> str:
    """Formatea watts. Bajo 10 W muestra un decimal; arriba, entero."""
    if w is None:
        return "--"
    if w < 0:
        w = 0.0
    if w < 10:
        return f"{w:.1f}W"
    return f"{w:.0f}W"


def fmt_pct(p: Optional[float]) -> str:
    """Formatea porcentaje entero (ej. '46%'). None -> '--'."""
    if p is None:
        return "--"
    return f"{p:.0f}%"


def is_high(value: Optional[float], threshold: float = 85.0) -> bool:
    """True si el valor supera el umbral de 'uso alto' (para resaltar en rojo)."""
    return value is not None and value >= threshold


def fmt_temp(t: Optional[float]) -> str:
    """Temperatura en grados (ej. '65°'). None -> '--'."""
    if t is None:
        return "--"
    return f"{t:.0f}°"


def fmt_vram(used_mb: Optional[float]) -> str:
    """VRAM usada en GB (ej. '4.2G'). None -> '--'."""
    if used_mb is None:
        return "--"
    g = used_mb / 1024.0
    if g >= 10:
        return f"{g:.0f}G"
    return f"{g:.1f}G"
