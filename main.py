"""
================================================================================
  main.py – Script principal de inventario de equipos informáticos
================================================================================

FLUJO DE EJECUCIÓN:

  0. Toma el mutex de instancia única y carga el ``.env`` que viaja con la app.
  1. Recolecta información del equipo actual (hardware, red, SO, usuario,
     AnyDesk).
  2. Construye un objeto Computer con todos los datos.
  3. Persiste el registro en la base de datos local portátil:
     a) JSON local (legacy)  → ComputerRepositoryLocal
     b) SQLite local         → ComputerRepositorySQLite
     c) MySQL remoto         → ComputerRepositoryMySQL (solo con
        USE_MYSQL_REMOTE=true)

PORTABILIDAD
------------
La aplicación puede ejecutarse desde un pendrive. La base de datos, los logs y
el ``.env`` viven junto al ejecutable:

  {APP_DIR}\\data\\localStorage.db
  {APP_DIR}\\logs\\app.log
  {APP_DIR}\\.env

No se escribe nada en ``%LOCALAPPDATA%`` ni en el directorio de trabajo actual.

VARIABLES DE ENTORNO RELEVANTES
-------------------------------
  APP_DIR=                  Carpeta base (vacío = carpeta del ejecutable)
  SQLITE_PATH=              Ruta explícita de la BD (vacío = {APP_DIR}\\data)
  LOG_DIR=                  Carpeta de logs (vacío = {APP_DIR}\\logs)
  LOG_LEVEL=INFO
  USE_MYSQL_REMOTE=false    "true" activa el envío directo a MySQL (legacy)
  SINGLE_INSTANCE_SCOPE=local
  SINGLE_INSTANCE_STRICT=false
  PORTABLE_STRICT=false     true = abortar si los logs no caben en {APP_DIR}

USO
---
  GENERATE_TECH-SHEET.exe
  GENERATE_TECH-SHEET.exe --allow-multiple   (diagnóstico; omite el mutex)
  GENERATE_TECH-SHEET.exe --quiet            (sin diálogos ni consola)
  GENERATE_TECH-SHEET.exe --verbose          (logging DEBUG)
  GENERATE_TECH-SHEET.exe --diagnose         (fuente y valor de cada campo)

================================================================================
"""

import argparse
import json
import os
import sys

from dotenv import load_dotenv

from src.computer_builder import ComputerBuilder
from src.infra.diagnostics import diagnostics
from src.infra.logging import configure_logging, get_logger
from src.infra.paths import (
    PortablePathError,
    ensure_parent_writable,
    env_file,
    migrate_legacy_sqlite,
    sqlite_path,
)
from src.infra.single_instance import (
    ERROR_ACCESS_DENIED,
    SingleInstance,
    resolve_mutex_name,
)
from src.modules.mod_anydesk import AnyDeskInfo
from src.modules.mod_hardware import HardwareInfo
from src.modules.mod_network import NetworkInfo
from src.modules.mod_os import OperativeSystem
from src.modules.mod_user import UserInformation
from src.notifications.popup import PopUp, PopUpError, PopUpWarning
from src.repository.computer_repository import ComputerRepositoryLocal
from src.repository.computer_repository_sqlite import ComputerRepositorySQLite

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_CONFIG = 2
EXIT_ALREADY_RUNNING = 75


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="GENERATE_TECH-SHEET",
        description="Genera la ficha técnica del equipo actual.",
    )
    parser.add_argument(
        "--allow-multiple",
        action="store_true",
        help="omite el mutex de instancia única (solo diagnóstico)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="no muestra diálogos ni escribe en consola",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="activa logging DEBUG",
    )
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help="muestra la fuente y el valor de cada campo, sin guardar nada",
    )
    return parser.parse_args(argv)


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name, "").strip().lower()
    if not value:
        return default
    return value in {"1", "true", "yes", "on", "si", "sí"}


def _acquire_mutex(args: argparse.Namespace) -> tuple[SingleInstance | None, bool]:
    """Intenta tomar el mutex; devuelve (instancia, adquirido)."""
    if args.allow_multiple:
        return None, True

    scope = os.getenv("SINGLE_INSTANCE_SCOPE", "local").strip().lower()
    instance = SingleInstance(resolve_mutex_name(scope))
    if instance.acquire():
        return instance, True

    # Global puede fallar por privilegios: degradar a Local sin bloquear.
    if scope == "global" and instance.last_error == ERROR_ACCESS_DENIED:
        fallback = SingleInstance(resolve_mutex_name("local"))
        if fallback.acquire():
            return fallback, True
        instance = fallback

    return instance, False


def _build_computer():
    """Instancia los proveedores y construye la ficha del equipo actual."""
    return ComputerBuilder(
        anydesk_provider=AnyDeskInfo(),
        user_provider=UserInformation(),
        hardware_provider=HardwareInfo(),
        system_provider=OperativeSystem(),
        network_provider=NetworkInfo(),
    ).create_computer()


def _diagnose(log) -> int:
    """Imprime fuentes, valores e incidencias sin persistir nada."""
    diagnostics.clear()
    computer = _build_computer()
    payload = diagnostics.as_dict()
    payload["computer"] = computer.to_dictionary()
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    print(text)
    log.info("Diagnóstico ejecutado: %s", ", ".join(sorted(payload["sources"])))
    return EXIT_OK


def _run(args: argparse.Namespace, log) -> int:
    # ------------------------------------------------------------------
    # PASO 1: Cargar registros existentes desde JSON (legacy)
    # ------------------------------------------------------------------
    local_repo = ComputerRepositoryLocal()
    current_computer_list = local_repo.create_computer_list()

    # ------------------------------------------------------------------
    # PASO 2: Recolectar información del equipo actual
    # ------------------------------------------------------------------
    diagnostics.clear()
    new_computer = _build_computer()

    # ------------------------------------------------------------------
    # PASO 3: Actualizar/insertar en JSON local (legacy)
    # ------------------------------------------------------------------
    updated_computer_list = local_repo.find_and_update_by_mac(
        current_computer_list, new_computer
    )
    local_repo.save_data_in_file(updated_computer_list)

    # ------------------------------------------------------------------
    # PASO 4: Persistir en SQLite (fuente de verdad local portátil)
    # ------------------------------------------------------------------
    db_file = sqlite_path()
    ensure_parent_writable(db_file)
    if migrate_legacy_sqlite() is not None:
        log.info("Base de datos legacy migrada a %s", db_file)
    sql_repo = ComputerRepositorySQLite(str(db_file))
    sql_repo.find_and_update_by_mac(new_computer)
    log.info("Ficha guardada en SQLite: %s", db_file)

    # ------------------------------------------------------------------
    # PASO 5: Enviar a MySQL remoto solo si está habilitado (legacy)
    # ------------------------------------------------------------------
    if _env_flag("USE_MYSQL_REMOTE"):
        # Import perezoso: MySQL es legacy y no debe impedir arrancar sin el
        # conector instalado cuando la sincronización remota está desactivada.
        from src.repository.computer_repository_mysql import ComputerRepositoryMySQL

        mysql_repo = ComputerRepositoryMySQL()
        mysql_repo.find_and_update_by_mac(new_computer)
        mysql_repo.close()

    # ------------------------------------------------------------------
    # PASO 6: Notificación final al usuario
    # ------------------------------------------------------------------
    log.info("Inventario completado para %s", new_computer.device_name)
    if not args.quiet:
        PopUp("Aviso", "¡Ficha guardada correctamente!")

    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    # El .env viaja con la aplicación, no se busca en el directorio actual.
    load_dotenv(dotenv_path=env_file())

    instance, acquired = _acquire_mutex(args)
    if not acquired:
        message = "El inventario ya se está generando en otra instancia."
        if not args.quiet:
            print(message, file=sys.stderr)
            PopUpWarning("Ya en ejecución", message)
        return EXIT_ALREADY_RUNNING if _env_flag("SINGLE_INSTANCE_STRICT") else EXIT_OK

    try:
        try:
            log_file = configure_logging(verbose=args.verbose, quiet=args.quiet)
        except PortablePathError as exc:
            if not args.quiet:
                PopUpError("Error de configuración", str(exc))
            print(f"No se pudo inicializar el logging: {exc}", file=sys.stderr)
            return EXIT_CONFIG

        log = get_logger("main")
        log.info("Inicio de la aplicación (log: %s)", log_file)
        if args.diagnose:
            return _diagnose(log)
        return _run(args, log)
    except PortablePathError as exc:
        if not args.quiet:
            PopUpError("Error de portabilidad", str(exc))
        print(str(exc), file=sys.stderr)
        return EXIT_CONFIG
    except Exception as exc:  # noqa: BLE001 - frontera de la aplicación
        get_logger("main").exception("Error no controlado")
        if not args.quiet:
            PopUpError("Error inesperado", f"No se pudo completar el inventario: {exc}")
        return EXIT_ERROR
    finally:
        if instance is not None:
            instance.release()


if __name__ == "__main__":
    raise SystemExit(main())
