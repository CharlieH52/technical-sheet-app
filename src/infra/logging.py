"""Logging unificado y portátil.

Sustituye el ``ErrorLogger`` que escribía en ``os.getcwd()``. Los archivos van
a ``{APP_DIR}\\logs`` (o a ``LOG_DIR``) y rotan para no crecer sin control.
Si la carpeta no es escribible se usa ``%TEMP%\\TechnicalSheet\\logs`` salvo
que ``PORTABLE_STRICT=true``, en cuyo caso se aborta.
"""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.infra import paths

_LOGGER_NAME = "technical_sheet"
_log_file: Path | None = None
_configured = False
_LOG_FORMAT = "%(asctime)s %(levelname)-5s [%(name)s] %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_MAX_BYTES = 1_000_000
_BACKUP_COUNT = 5


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name, "").strip().lower()
    if not value:
        return default
    return value in {"1", "true", "yes", "on", "si", "sí"}


def _resolve_level(verbose: bool) -> int:
    if verbose:
        return logging.DEBUG
    name = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    return getattr(logging, name, logging.INFO)


def configure_logging(*, verbose: bool = False, quiet: bool = False) -> Path:
    """Configura el logger raíz de la aplicación y devuelve la ruta del log.

    Args:
        verbose: fuerza nivel ``DEBUG``.
        quiet: no escribe en consola (el archivo se sigue generando).

    Raises:
        PortablePathError: si ``PORTABLE_STRICT=true`` y no se puede escribir.
    """
    global _log_file, _configured

    if _configured and _log_file is not None:
        return _log_file

    strict = _env_flag("PORTABLE_STRICT")
    try:
        directory = paths.ensure_writable_dir(paths.log_dir())
        log_file = directory / "app.log"
    except paths.PortablePathError:
        if strict:
            raise
        directory = paths.ensure_writable_dir(paths.temp_log_dir())
        log_file = directory / "app.log"

    formatter = logging.Formatter(_LOG_FORMAT, _DATE_FORMAT)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(_resolve_level(verbose))
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    logger.addHandler(file_handler)
    logger.propagate = False

    # Consola solo en desarrollo o si se pide explícitamente.
    if not quiet and (verbose or not getattr(sys, "frozen", False)):
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)

    _log_file = log_file
    _configured = True
    return log_file


def get_logger(name: str = "") -> logging.Logger:
    """Devuelve un logger hijo, configurando el logging si aún no se hizo."""
    if not _configured:
        configure_logging()
    suffix = f".{name}" if name else ""
    return logging.getLogger(f"{_LOGGER_NAME}{suffix}")


def current_log_path() -> Path:
    """Ruta del ``app.log`` activo."""
    if not _configured:
        configure_logging()
    assert _log_file is not None
    return _log_file


def clear_log_files() -> None:
    """Elimina ``app.log`` y sus rotaciones.

    En Windows el ``RotatingFileHandler`` mantiene el archivo abierto, así que
    primero se cierran los handlers y después se borran los archivos. El
    logging se reconfigura de forma perezosa en el siguiente ``get_logger``.
    """
    if not _configured:
        configure_logging()
    assert _log_file is not None

    log_file = _log_file
    candidates = [
        log_file,
        *(log_file.with_name(f"{log_file.name}.{i}") for i in range(1, _BACKUP_COUNT + 1)),
    ]
    reset_logging()
    for candidate in candidates:
        try:
            candidate.unlink(missing_ok=True)
        except OSError:
            # Un archivo bloqueado por otro proceso no debe romper el cierre.
            pass


def reset_logging() -> None:
    """Reinicia la configuración global (tests o cambios en caliente)."""
    global _log_file, _configured

    logger = logging.getLogger(_LOGGER_NAME)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    _log_file = None
    _configured = False
