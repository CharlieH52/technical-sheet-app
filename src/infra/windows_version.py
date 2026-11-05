"""Normalización de la versión de Windows desde el registro.

El registro puede mentir: en Windows 11 es habitual que ``ProductName`` siga
diciendo "Windows 10". La fuente fiable es ``CurrentBuild`` (>= 22000 es
Windows 11). Aquí se corrige y se formatea el texto que consume la ficha.
"""

from __future__ import annotations

import platform
import re
from dataclasses import dataclass

from src.infra import registry

try:  # pragma: no cover - solo Windows
    import winreg

    _HKLM = winreg.HKEY_LOCAL_MACHINE
except ImportError:  # pragma: no cover
    _HKLM = 0

_VERSION_KEY = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
_WINDOWS_11_BUILD = 22000

_EDITION_NAMES = {
    "Professional": "Pro",
    "ProfessionalN": "Pro N",
    "Core": "Home",
    "CoreN": "Home N",
    "CoreSingleLanguage": "Home Single Language",
    "CoreCountrySpecific": "Home",
    "Education": "Education",
    "EducationN": "Education N",
    "Enterprise": "Enterprise",
    "EnterpriseN": "Enterprise N",
    "EnterpriseS": "Enterprise LTSC",
    "IoTEnterprise": "IoT Enterprise",
    "ServerStandard": "Server Standard",
    "ServerDatacenter": "Server Datacenter",
}


def _clean(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).replace("\x00", " ").strip()
    return re.sub(r"\s+", " ", text) or None


def _to_int(value: object) -> int | None:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def normalize_architecture(machine: str | None) -> str:
    """Normaliza ``platform.machine()`` a ``x64``, ``x86`` o ``ARM64``."""
    value = (machine or "").strip().lower()
    if value in {"amd64", "x86_64", "x64"}:
        return "x64"
    if value in {"arm64", "aarch64"}:
        return "ARM64"
    if value in {"x86", "i386", "i686"}:
        return "x86"
    return machine or "desconocida"


def normalize_product_name(
    product_name: str | None,
    build: int | None,
    edition_id: str | None = None,
) -> str:
    """Corrige el nombre del producto y evita el "Windows 10" falso."""
    name = _clean(product_name)
    if name:
        if name.lower().startswith("microsoft "):
            name = name[len("microsoft ") :]
        if build is not None and build >= _WINDOWS_11_BUILD:
            name = re.sub(r"windows 10", "Windows 11", name, flags=re.IGNORECASE)
        return name

    family = "Windows 11" if (build or 0) >= _WINDOWS_11_BUILD else "Windows 10"
    edition = _EDITION_NAMES.get(edition_id or "", edition_id)
    return f"{family} {edition}".strip()


def format_windows_version(
    product: str,
    build: int | None = None,
    ubr: int | None = None,
    display_version: str | None = None,
) -> str:
    """Formatea ``Windows 11 Pro 26H2 (26300.9711)`` y limita a 100 caracteres."""
    parts = [part for part in (product, display_version) if part]
    if build is not None:
        parts.append(f"({build}.{ubr})" if ubr is not None else f"({build})")
    return " ".join(parts)[:100]


@dataclass(frozen=True)
class WindowsVersionInfo:
    product: str
    architecture: str
    build: int | None
    ubr: int | None
    display_version: str | None
    edition: str | None
    source: str

    @property
    def formatted(self) -> str:
        return format_windows_version(
            self.product,
            self.build,
            self.ubr,
            self.display_version,
        )


def read_windows_version() -> WindowsVersionInfo:
    """Lee la versión desde el registro con fallback a ``platform``."""
    product = _clean(registry.read_value(_HKLM, _VERSION_KEY, "ProductName"))
    build = _to_int(registry.read_value(_HKLM, _VERSION_KEY, "CurrentBuild"))
    if build is None:
        build = _to_int(registry.read_value(_HKLM, _VERSION_KEY, "CurrentBuildNumber"))
    ubr = _to_int(registry.read_value(_HKLM, _VERSION_KEY, "UBR"))
    display_version = _clean(registry.read_value(_HKLM, _VERSION_KEY, "DisplayVersion"))
    if display_version is None:
        display_version = _clean(registry.read_value(_HKLM, _VERSION_KEY, "ReleaseId"))
    edition = _clean(registry.read_value(_HKLM, _VERSION_KEY, "EditionID"))
    architecture = normalize_architecture(platform.machine())

    source = "registry" if (product or build) else "platform"
    if not product:
        product = normalize_product_name(None, build, edition)
    else:
        product = normalize_product_name(product, build, edition)

    return WindowsVersionInfo(
        product=product,
        architecture=architecture,
        build=build,
        ubr=ubr,
        display_version=display_version,
        edition=edition,
        source=source,
    )
