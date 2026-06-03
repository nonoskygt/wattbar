# ⚡ WattBar

**Monitor de energía y sistema para la barra de tareas de Windows 11.** Estilo
*Traffic Monitor*, pero enfocado en los **watts** de tu equipo: cuánto **entra**
(carga), cuánto **sale** (consumo), más CPU, RAM, GPU, VRAM y temperaturas — todo
en una tira fina, siempre visible, que se actualiza cada segundo.

![WattBar en 2 líneas](docs/img/wattbar_2lines.png)

> En una línea:
>
> ![WattBar en 1 línea](docs/img/wattbar_1line.png)

---

## ✨ Qué muestra

| Campo | Significado | Fuente |
|-------|-------------|--------|
| **⚡ PC** | Consumo total real del equipo (W) | A batería: descarga real · Enchufado: CPU+GPU+base autocalibrada (`~`) |
| **BAT ↓ / ↑** | Watts que **entran** (carga) / **salen** (consumo) de la batería | WMI `BatteryStatus` |
| **CPU / MEM / GPU %** | Uso de CPU, RAM y GPU | `psutil` + NVML |
| **VRAM** | Memoria de video usada (GB) | NVML |
| **CPU° / GPU°** | Temperatura de CPU y GPU | LibreHardwareMonitor / NVML |

Los valores altos de uso o temperatura se **resaltan en rojo**. Cada campo se puede
mostrar u ocultar, y la tira admite **1 o 2 líneas**.

## 🔌 Cómo funciona

WattBar lee sensores **reales** del sistema, no estima a ciegas:

- **Watts de batería** (entra/sale): WMI `root\wmi BatteryStatus` (`ChargeRate` /
  `DischargeRate`, en mW). A batería, la descarga **es** el consumo total real del equipo.
- **CPU % / RAM %**: `psutil`.
- **GPU % / VRAM / temp. GPU / watts GPU**: NVML (`nvidia-ml-py`), sin lanzar procesos.
- **Watts y temperatura de CPU**: [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor)
  vía su servidor web JSON (`localhost:8085`). Windows no expone la potencia del CPU a
  apps normales; LHM la lee del chip (RAPL) con su driver.

**Consumo total estando enchufado:** a batería, WattBar conoce el consumo exacto
(descarga) y **aprende** cuánto pesa "el resto" (pantalla, RAM, SSD…). Reutiliza esa
base calibrada al estar enchufado, sumándola a la potencia real de CPU+GPU. Por eso el
número enchufado lleva un `~`: es estimado, pero anclado a mediciones reales.

## 📦 Requisitos

- Windows 10 / 11
- Python 3.11+
- GPU NVIDIA — opcional (para GPU %, VRAM y temp. de GPU)
- LibreHardwareMonitor corriendo — opcional (para watts y temp. de CPU)

## 🚀 Instalación

```powershell
pip install -r requirements.txt
```

> `PySide6`, `pywin32`, `psutil`, `wmi`, `nvidia-ml-py`

### Consumo y temperatura de CPU (LibreHardwareMonitor)

1. Instalá LHM: `winget install LibreHardwareMonitor.LibreHardwareMonitor`
2. Ejecutalo **como administrador** (necesario para leer la potencia del CPU).
3. Activá el servidor web: menú **Options → Remote Web Server → Run** (puerto 8085).

Sin LHM, WattBar igual funciona: muestra flujo de batería, CPU/RAM/GPU/VRAM y temp. de GPU.

## ▶️ Uso

```powershell
pythonw run.pyw
```

- **Clic derecho** en la tira (o en el ícono ⚡ de la bandeja) → **Configuración**:
  elegí el **modo**, 1/2 líneas, qué campos mostrar, tamaño de fuente, ocultar en
  pantalla completa e **Iniciar con Windows**.
- **Dos modos:**
  - **Integrado en la barra** (estilo *Traffic Monitor*): la tira va dentro de la
    franja de la barra de tareas, a la derecha. Posición fija.
  - **Flotante**: ventana libre, **arrastrable** a cualquier monitor (recuerda la posición).
- Se **oculta sola** cuando una app va a pantalla completa (juegos / video).

## ⚙️ Configuración

Se guarda en `%APPDATA%\WattBar\config.json`: campos visibles, layout (1/2 líneas),
tamaño de fuente, colores, posición, puerto de LHM y la base de consumo autocalibrada.

## 🧱 Arquitectura

```
wattbar/
  sensors/   battery · system · gpu · power (LHM) · hub (Snapshot)
  ui/        bar (la tira) · settings · theme (formato)
  win/       taskbar (posición / pantalla completa) · tray · autostart
  app.py     QTimer(1s) → hub.read() → bar.update_data()
```

Flujo de datos: `QTimer(1 s) → SensorHub.read() → Snapshot → WattBar.update_data()`.
Cada sensor es tolerante a fallos: si una fuente no está, devuelve `--` sin tirar la app.

## 📝 Notas

- **Consumo:** enchufado y con batería llena, el flujo de batería marca ~0 W (no entra
  ni sale energía de la batería). El consumo total directo solo se mide a batería;
  enchufado se estima con CPU+GPU reales + base calibrada.
- **Windows 11:** su barra de tareas es XAML y no admite incrustar ventanas de otras
  apps vía `SetParent` (la ventana termina fuera de pantalla). Por eso el modo
  *integrado en la barra* se logra con una tira flotante *always-on-top* posicionada
  dentro de la franja de la barra: se ve igual, es robusto y multi-monitor.

## 🧪 Tests

```powershell
python -m pytest -q
```

## 📄 Licencia

[MIT](LICENSE).
