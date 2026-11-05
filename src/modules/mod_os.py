"""Información del sistema operativo sin PowerShell.

Lee el registro con ``winreg``, corrige el falso "Windows 10" de los equipos
Windows 11 usando ``CurrentBuild`` y normaliza la arquitectura.
"""

from src.infra.diagnostics import diagnostics
from src.infra.windows_version import read_windows_version


class OperativeSystem:

    def __init__(self):
        self.info = read_windows_version()
        diagnostics.record(
            "operative_system",
            self.info.formatted,
            self.info.source,
            note=f"build={self.info.build} ubr={self.info.ubr} edition={self.info.edition}",
        )

    def win_product(self) -> str:
        """Nombre del producto ya corregido (p. ej. Windows 11 Pro)."""
        return self.info.product

    def win_architecture(self) -> str:
        """Arquitectura normalizada: x64, x86 o ARM64."""
        return self.info.architecture

    def get_windows_version(self) -> str:
        """Texto final de la ficha: Windows 11 Pro 26H2 (26300.9711)."""
        return self.info.formatted
