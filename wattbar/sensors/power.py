"""Potencia real de CPU/GPU desde el servidor web JSON de LibreHardwareMonitor.

LHM corriendo elevado y con `Options > Remote Web Server > Run` sirve todos los
sensores en http://localhost:8085/data.json. Recorremos el árbol y tomamos los
nodos de tipo 'Power' del paquete de CPU y de la GPU.

Si LHM no está corriendo o el servidor está apagado, `read()` devuelve None y la
app sigue funcionando con el flujo de batería.
"""
import json
import urllib.request


def _parse_watts(val):
    """'45.2 W' / '45,2 W' -> 45.2 (float) ; None si no parsea."""
    if val is None:
        return None
    s = str(val).replace(",", ".")
    num = ""
    for ch in s:
        if ch.isdigit() or ch in ".-":
            num += ch
        elif num:
            break
    try:
        return float(num)
    except ValueError:
        return None


def _walk(node, out):
    if not isinstance(node, dict):
        return
    t = node.get("Type")
    if t in ("Power", "Temperature"):
        out.append((
            t,
            str(node.get("SensorId", "")),
            str(node.get("Text", "")),
            node.get("Value", ""),
        ))
    for ch in node.get("Children", []) or []:
        _walk(ch, out)


class LhmPowerSensor:
    def __init__(self, port=8085, timeout=0.4):
        self._url = "http://localhost:%d/data.json" % port
        self._timeout = timeout

    def read(self):
        """Devuelve {'cpu_watts': float|None, 'gpu_watts': float|None} o None."""
        try:
            with urllib.request.urlopen(self._url, timeout=self._timeout) as resp:
                data = json.loads(resp.read().decode("utf-8", "ignore"))
        except Exception:
            return None
        sensors = []
        _walk(data, sensors)
        cpu = gpu_package = gpu_power = cpu_temp = None
        for typ, sid, text, val in sensors:
            num = _parse_watts(val)
            if num is None:
                continue
            s, t = sid.lower(), text.lower()
            if typ == "Power":
                if "cpu" in s and "package" in t:
                    cpu = num
                elif "gpu" in s and "package" in t:
                    gpu_package = num
                elif "gpu" in s and "power" in t:
                    gpu_power = num
            elif typ == "Temperature":
                if "cpu" in s and "package" in t:
                    cpu_temp = num
        # Preferir "GPU Package" sobre "GPU Power" (que en NVIDIA suele ser 0).
        gpu = gpu_package if gpu_package is not None else gpu_power
        if cpu is None and gpu is None and cpu_temp is None:
            return None
        return {"cpu_watts": cpu, "gpu_watts": gpu, "cpu_temp": cpu_temp}


if __name__ == "__main__":
    print(LhmPowerSensor().read())
