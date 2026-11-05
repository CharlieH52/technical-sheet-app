"""Rutas portátiles de la aplicación.

Regla de diseño: todo (base de datos, logs y ``.env``) vive junto al
ejecutable. Nunca se usa el directorio de trabajo actual ni ``%LOCALAPPDATA%``,
porque la aplicación puede ejecutarse desde un pendrive y no debe dejar
rastros en el equipo que se está inventariando.

Variables de entorno reconocidas:

* ``APP_DIR``: carpeta base de la aplicación. Vacía = carpeta del ejecutable
  (o raíz del repositorio en desarrollo).
* ``SQLITE_PATH``: ruta explícita de la base SQLite. Vacía =
  ``{APP_DIR}\\data\\localStorage.db``.
* ``LOG_DIR``: carpeta de logs. Vacía = ``{APP_DIR}\\logs``.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path


class PortablePathError(RuntimeError):
    """La ruta portátil no existe o no se puede escribir."""


def default_app_dir() -> Path:
    """Carpeta del ejecutable empaquetado o raíz del repositorio en desarrollo."""
    if getattr(sys, "frozen", False):  # PyInstaller
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def _resolve_from_app(value: str) -> Path:
    """Resuelve una ruta absoluta o relativa a la carpeta de la aplicación."""
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = default_app_dir() / path
    return path.resolve()


def _env_path(name: str) -> Path | None:
    value = os.getenv(name, "").strip()
    return _resolve_from_app(value) if value else None


def app_dir() -> Path:
    """Carpeta base de la aplicación."""
    return _env_path("APP_DIR") or default_app_dir()


def data_dir() -> Path:
    """Carpeta de datos portátiles."""
    return app_dir() / "data"


def log_dir() -> Path:
    """Carpeta de logs portátiles."""
    return _env_path("LOG_DIR") or (app_dir() / "logs")


def sqlite_path() -> Path:
    """Ruta de la base SQLite local."""
    return _env_path("SQLITE_PATH") or (data_dir() / "localStorage.db")


def env_file() -> Path:
    """Ruta del ``.env`` que viaja con la aplicación."""
    return app_dir() / ".env"


def temp_log_dir() -> Path:
    """Fallback de logs cuando ``{APP_DIR}`` no es escribible."""
    return Path(tempfile.gettempdir()) / "TechnicalSheet" / "logs"


def ensure_writable_dir(path: Path) -> Path:
    """Crea ``path`` si hace falta y comprueba que se puede escribir en ella.

    Lanza :class:`PortablePathError` con un mensaje accionable si no es posible.
    """
    path = Path(path)
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / f".write-test-{os.getpid()}"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except OSError as exc:
        raise PortablePathError(
            f"No se puede escribir en '{path}'. Copie la aplicación a una "
            f"carpeta con permisos de escritura o configure APP_DIR, "
            f"SQLITE_PATH o LOG_DIR. Detalle: {exc}"
        ) from exc
    return path


def ensure_parent_writable(path: Path) -> Path:
    """Garantiza que la carpeta contenedora de ``path`` existe y es escribible."""
    return ensure_writable_dir(Path(path).resolve().parent)


def ensure_data_dir() -> Path:
    """Crea y valida la carpeta de datos portátiles."""
    return ensure_writable_dir(data_dir())


def ensure_log_dir() -> Path:
    """Crea y valida la carpeta de logs portátiles."""
    return ensure_writable_dir(log_dir())


def migrate_legacy_sqlite() -> Path | None:
    """Copia la BD antigua de la raíz a la carpeta portátil ``data``.

    Solo actúa cuando se usa la ruta por defecto (``SQLITE_PATH`` vacío) y el
    destino aún no existe. Devuelve la ruta migrada o ``None`` si no hubo nada
    que migrar. El archivo original se conserva como respaldo.
    """
    if _env_path("SQLITE_PATH"):
        return None

    target = sqlite_path()
    if target.exists():
        return None

    legacy = app_dir() / "localStorage.db"
    if not legacy.exists() or legacy.resolve() == target.resolve():
        return None

    ensure_parent_writable(target)
    shutil.copy2(legacy, target)
    return target
