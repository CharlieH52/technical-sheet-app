"""Conversiones de unidades usadas por los módulos de captura."""

from __future__ import annotations

_GIB = 1024 ** 3
_MIB = 1024 ** 2


def bytes_to_gib(total_bytes: int | None) -> int | None:
    """Convierte bytes a GiB enteros (redondeo por truncamiento)."""
    if total_bytes is None:
        return None
    try:
        return int(total_bytes) // _GIB
    except (TypeError, ValueError):
        return None


def bytes_to_mib(total_bytes: int | None) -> int | None:
    """Convierte bytes a MiB enteros."""
    if total_bytes is None:
        return None
    try:
        return int(total_bytes) // _MIB
    except (TypeError, ValueError):
        return None
