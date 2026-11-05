"""Instancia única mediante un mutex con nombre del kernel de Windows.

El sistema libera el mutex cuando el proceso termina, incluso si muere de forma
abrupta, así que no quedan bloqueos huérfanos como ocurre con un archivo
``.lock``.
"""

from __future__ import annotations

import ctypes
import os
from ctypes import wintypes

ERROR_ALREADY_EXISTS = 183
ERROR_ACCESS_DENIED = 5
MUTEX_BASENAME = "TechnicalSheet.App.v1"


def resolve_mutex_name(scope: str | None = None) -> str:
    """Devuelve el nombre completo del mutex según el ámbito configurado.

    ``local`` (por defecto) no requiere privilegios. ``global`` abarca todo el
    equipo y puede fallar con ``ERROR_ACCESS_DENIED``.
    """
    selected = (scope or os.getenv("SINGLE_INSTANCE_SCOPE", "local")).strip().lower()
    prefix = "Global\\" if selected == "global" else "Local\\"
    return f"{prefix}{MUTEX_BASENAME}"


class SingleInstance:
    """Mutex de instancia única.

    ``acquire()`` devuelve ``True`` si esta instancia obtuvo el mutex. Si ya
    había otra instancia, devuelve ``False`` y deja ``last_error`` con el
    código de Windows (útil para distinguir ``ERROR_ACCESS_DENIED``).
    """

    def __init__(self, name: str | None = None):
        self._name = name or resolve_mutex_name()
        self._handle: int | None = None
        self.last_error: int | None = None

    @property
    def name(self) -> str:
        return self._name

    def acquire(self) -> bool:
        # Permite ejecutar los tests en plataformas no Windows.
        if os.name != "nt":
            return True

        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateMutexW.argtypes = (wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR)
        k32.CreateMutexW.restype = wintypes.HANDLE
        k32.CloseHandle.argtypes = (wintypes.HANDLE,)
        k32.CloseHandle.restype = wintypes.BOOL

        handle = k32.CreateMutexW(None, False, self._name)
        error = ctypes.get_last_error()
        self.last_error = error or None

        if not handle:
            # No se pudo crear el mutex: no bloquear la aplicación por ello.
            return False

        if error == ERROR_ALREADY_EXISTS:
            k32.CloseHandle(handle)
            return False

        self._handle = handle
        return True

    def release(self) -> None:
        if self._handle is None or os.name != "nt":
            return

        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CloseHandle.argtypes = (wintypes.HANDLE,)
        k32.CloseHandle.restype = wintypes.BOOL
        k32.CloseHandle(self._handle)
        self._handle = None
