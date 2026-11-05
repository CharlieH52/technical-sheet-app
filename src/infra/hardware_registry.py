"""CPU y placa base desde el registro de Windows (sin PowerShell)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from src.infra import registry

try:  # pragma: no cover - solo Windows
    import winreg

    _HKLM = winreg.HKEY_LOCAL_MACHINE
except ImportError:  # pragma: no cover
    _HKLM = 0

_BIOS_KEY = r"HARDWARE\DESCRIPTION\System\BIOS"
_CPU_KEY = r"HARDWARE\DESCRIPTION\System\CentralProcessor\{index}"


def _clean(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).replace("\x00", " ").strip()
    return re.sub(r"\s+", " ", text) or None


@dataclass(frozen=True)
class MotherboardInfo:
    manufacturer: str | None
    product: str | None
    version: str | None
    source: str


def read_motherboard() -> MotherboardInfo:
    """Lee fabricante, modelo y versión de la placa desde el registro."""
    manufacturer = _clean(registry.read_value(_HKLM, _BIOS_KEY, "BaseBoardManufacturer"))
    product = _clean(registry.read_value(_HKLM, _BIOS_KEY, "BaseBoardProduct"))
    version = _clean(registry.read_value(_HKLM, _BIOS_KEY, "BaseBoardVersion"))
    source = "registry" if (manufacturer or product) else "none"
    return MotherboardInfo(
        manufacturer=manufacturer,
        product=product,
        version=version,
        source=source,
    )


def read_cpu_name() -> tuple[str | None, str]:
    """Devuelve el nombre comercial de la CPU y la fuente usada."""
    for index in range(8):
        name = _clean(
            registry.read_value(
                _HKLM,
                _CPU_KEY.format(index=index),
                "ProcessorNameString",
            )
        )
        if name:
            return name, "registry"

    identifier = _clean(os.getenv("PROCESSOR_IDENTIFIER"))
    if identifier:
        return identifier, "environment"
    return None, "none"
