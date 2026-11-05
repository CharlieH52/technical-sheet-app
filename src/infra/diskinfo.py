"""Detección del disco del sistema con ``psutil`` y ``%SystemDrive%``."""

from __future__ import annotations

import os
from dataclasses import dataclass

import psutil


@dataclass(frozen=True)
class SystemDiskInfo:
    """Datos del disco/partición donde arranca Windows."""

    drive: str
    mountpoint: str | None
    device: str | None
    fstype: str | None
    total_bytes: int | None
    used_bytes: int | None
    free_bytes: int | None
    source: str


def system_drive() -> str:
    """Devuelve la letra del disco del sistema (p. ej. ``C:``)."""
    value = (os.getenv("SystemDrive") or "C:").strip().rstrip("\\/")
    return value or "C:"


def read_system_disk() -> SystemDiskInfo:
    """Lee la partición y el uso del disco del sistema.

    Si la partición no se encuentra en ``psutil.disk_partitions()``, se intenta
    al menos con ``psutil.disk_usage()`` para el punto de montaje.
    """
    drive = system_drive()
    mountpoint = f"{drive}\\"
    try:
        partitions = psutil.disk_partitions(all=False)
        match = None
        target = os.path.normcase(os.path.normpath(mountpoint))
        for part in partitions:
            if os.path.normcase(os.path.normpath(part.mountpoint)) == target:
                match = part
                break

        usage = psutil.disk_usage(mountpoint)
        return SystemDiskInfo(
            drive=drive,
            mountpoint=mountpoint,
            device=match.device if match else None,
            fstype=match.fstype if match else None,
            total_bytes=int(usage.total),
            used_bytes=int(usage.used),
            free_bytes=int(usage.free),
            source="environment+psutil",
        )
    except Exception:  # noqa: BLE001 - psutil puede fallar en equipos sin permisos
        return SystemDiskInfo(
            drive=drive,
            mountpoint=mountpoint,
            device=None,
            fstype=None,
            total_bytes=None,
            used_bytes=None,
            free_bytes=None,
            source="environment",
        )
