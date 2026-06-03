"""Lanzador sin consola (doble clic o autostart). Usar con pythonw.exe."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wattbar.app import main

main()
