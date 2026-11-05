"""Lectura genérica del registro de Windows.

Centraliza ``winreg`` para que los módulos no manipulen claves directamente y
puedan degradar a ``None`` cuando un valor no existe o el equipo no es Windows.
"""

from __future__ import annotations

from typing import Any

try:  # pragma: no cover - solo se ejecuta en Windows
    import winreg
except ImportError:  # pragma: no cover
    winreg = None


def _access(view: int) -> int:
    access = winreg.KEY_READ  # type: ignore[union-attr]
    if view == 64:
        access |= winreg.KEY_WOW64_64KEY  # type: ignore[union-attr]
    elif view == 32:
        access |= winreg.KEY_WOW64_32KEY  # type: ignore[union-attr]
    return access


def read_value(
    root: int,
    path: str,
    name: str,
    *,
    default: Any = None,
    view: int = 64,
) -> Any:
    """Lee un valor del registro y devuelve ``default`` si no está disponible."""
    if winreg is None:
        return default
    try:
        with winreg.OpenKey(root, path, 0, _access(view)) as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value
    except OSError:
        return default


def read_many(
    root: int,
    path: str,
    names: tuple[str, ...],
    *,
    view: int = 64,
) -> dict[str, Any]:
    """Lee varios valores de una misma clave."""
    return {name: read_value(root, path, name, view=view) for name in names}


def read_dword(root: int, path: str, name: str, *, view: int = 64) -> int | None:
    """Lee un valor entero (REG_DWORD) y lo normaliza."""
    value = read_value(root, path, name, view=view)
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
