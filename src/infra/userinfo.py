"""Identidad del usuario de la sesión (sin ``os.getlogin()``).

Se usan ``getpass.getuser()`` y ``USERDOMAIN`` (variable de entorno o registro
``Volatile Environment``), que no fallan cuando no hay consola adjunta.
"""

from __future__ import annotations

import getpass
import os
from dataclasses import dataclass

from src.infra import registry

try:  # pragma: no cover - solo Windows
    import winreg

    _HKCU = winreg.HKEY_CURRENT_USER
except ImportError:  # pragma: no cover
    _HKCU = 0

_VOLATILE_ENV = r"Volatile Environment"


@dataclass(frozen=True)
class UserIdentity:
    """Datos del usuario de la sesión actual."""

    username: str
    domain: str | None
    qualified: str
    source: str
    full_name: str | None = None


def _registry_value(name: str) -> str | None:
    value = registry.read_value(_HKCU, _VOLATILE_ENV, name)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def read_user_identity() -> UserIdentity:
    """Resuelve usuario/dominio sin depender de ``os.getlogin()``.

    Prioridad de usuario: ``getpass.getuser()`` → ``USERNAME`` → registro.
    Prioridad de dominio: ``USERDOMAIN`` → registro → ``None``.
    """
    username = getpass.getuser().strip()
    source = "getpass"

    if not username:
        username = os.getenv("USERNAME", "").strip()
        source = "environment"
    if not username:
        username = _registry_value("USERNAME") or ""
        source = "registry"

    domain = os.getenv("USERDOMAIN", "").strip()
    domain_source = "environment"
    if not domain:
        domain = _registry_value("USERDOMAIN")
        domain_source = "registry"

    if username and domain and domain.upper() != username.upper():
        qualified = f"{domain}\\{username}"
    else:
        qualified = username

    if domain_source == "registry" and source == "getpass":
        source = "getpass+registry"

    return UserIdentity(
        username=username,
        domain=domain or None,
        qualified=qualified,
        source=source,
        full_name=_registry_value("USERPROFILE"),
    )
