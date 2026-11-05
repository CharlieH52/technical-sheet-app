from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from src.models.computer import Computer
from src.models.ram import DimmRam
from src.models.storage import StorageDrive
from src.infra.logging import get_logger
from src.notifications.popup import PopUpWarning

try:
    from src.infra.netinfo import normalize_mac
except ImportError:  # pragma: no cover - psutil no disponible
    def normalize_mac(value):
        return value


class ComputerRepositorySQLite:
    """
    Repositorio de persistencia en SQLite para equipos informáticos.

    Mantiene una relación 1:N entre Computer (tabla principal) y DimmRam (tabla secundaria),
    usando machine_mac como clave primaria/foránea.
    """

    def __init__(self, db_path: str | Path | None = None):
        """
        Inicializa el repositorio SQLite.

        Args:
            db_path: Ruta al archivo .db. Si es None, usa la ruta portátil
                ``{APP_DIR}\\data\\localStorage.db`` (ver src.infra.paths).
        """
        if db_path is None:
            from src.infra.paths import sqlite_path

            db_path = sqlite_path()

        self.DB_NAME = str(db_path)
        self.WORKING_PATH = str(Path(self.DB_NAME).resolve().parent)

        # La BD debe poder crearse junto al ejecutable; si no, error claro
        # en lugar de una excepción opaca de sqlite3.
        from src.infra.paths import ensure_parent_writable

        ensure_parent_writable(Path(self.DB_NAME))
        self._init_database()

    @contextmanager
    def _get_connection(self) -> sqlite3.Connection:
        """Retorna una conexión a la base de datos con row_factory configurado.

        Se cierra automáticamente al salir del bloque ``with``, evitando que los
        archivos queden bloqueados en Windows (importante para tests y USB).
        """
        conn = sqlite3.connect(self.DB_NAME)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_database(self) -> None:
        """Crea las tablas si no existen."""
        create_computers_table = """
        CREATE TABLE IF NOT EXISTS computers (
            machine_mac TEXT PRIMARY KEY,
            device_name TEXT NOT NULL,
            user_name TEXT NOT NULL,
            machine_ip TEXT,
            mobo_mark TEXT,
            mobo_model TEXT,
            cpu_info TEXT,
            operative_system TEXT,
            storage_model TEXT,
            storage_cap INTEGER,
            anydesk_id INTEGER
        );
        """

        create_dimm_ram_table = """
        CREATE TABLE IF NOT EXISTS dimm_ram (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_mac TEXT NOT NULL,
            caption TEXT,
            manufacturer TEXT,
            part_number TEXT,
            model TEXT,
            tag TEXT,
            bank_label TEXT,
            device_locator TEXT,
            capacity INTEGER DEFAULT 0,
            speed INTEGER DEFAULT 0,
            configured_clock_speed INTEGER DEFAULT 0,
            configured_voltage INTEGER DEFAULT 0,
            FOREIGN KEY (machine_mac) REFERENCES computers(machine_mac)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
        """

        create_storage_drive_table = """
        CREATE TABLE IF NOT EXISTS storage_drive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_mac TEXT NOT NULL,
            device_id TEXT NOT NULL,
            model TEXT,
            serial_number TEXT,
            size_bytes INTEGER,
            interface_type TEXT,
            media_type TEXT,
            partitions INTEGER,
            drive_letters TEXT,
            is_system INTEGER DEFAULT 0,
            FOREIGN KEY (machine_mac) REFERENCES computers(machine_mac)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
        """

        create_index = """
        CREATE INDEX IF NOT EXISTS idx_dimm_mac ON dimm_ram(machine_mac);
        """

        create_storage_index = """
        CREATE INDEX IF NOT EXISTS idx_storage_mac ON storage_drive(machine_mac);
        """

        try:
            with self._get_connection() as conn:
                conn.execute(create_computers_table)
                conn.execute(create_dimm_ram_table)
                conn.execute(create_storage_drive_table)
                conn.execute(create_index)
                conn.execute(create_storage_index)
                conn.execute("PRAGMA user_version = 2;")
                conn.commit()
            self._migrate_legacy_macs()
            self._migrate_schema()
            self._migrate_schema()
        except sqlite3.Error as e:
            # La capa de datos no muestra diálogos: registra y deja que main
            # decida cómo informar (--quiet no debe abrir ventanas).
            get_logger("repository.sqlite").error(
                "No se pudo inicializar SQLite en %s: %s", self.DB_NAME, e
            )
            raise

    def _migrate_legacy_macs(self) -> None:
        """Migra MAC con guiones al formato normalizado con dos puntos."""
        logger = get_logger("repository.sqlite")
        try:
            with self._get_connection() as conn:
                rows = conn.execute("SELECT machine_mac FROM computers;").fetchall()
                for row in rows:
                    old_mac = row["machine_mac"]
                    new_mac = normalize_mac(old_mac)
                    if not new_mac or new_mac == old_mac:
                        continue

                    existing = conn.execute(
                        "SELECT 1 FROM computers WHERE machine_mac = ?;", (new_mac,)
                    ).fetchone()
                    if existing:
                        logger.warning(
                            "MAC %s ya existe en formato normalizado; se elimina %s",
                            new_mac,
                            old_mac,
                        )
                        conn.execute(
                            "DELETE FROM dimm_ram WHERE machine_mac = ?;", (old_mac,)
                        )
                        conn.execute(
                            "DELETE FROM computers WHERE machine_mac = ?;", (old_mac,)
                        )
                    else:
                        conn.execute(
                            "UPDATE computers SET machine_mac = ? WHERE machine_mac = ?;",
                            (new_mac, old_mac),
                        )
                        conn.execute(
                            "UPDATE dimm_ram SET machine_mac = ? WHERE machine_mac = ?;",
                            (new_mac, old_mac),
                        )
                conn.commit()
        except sqlite3.Error as exc:
            logger.error("No se pudo migrar el formato de MAC: %s", exc)

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------

    def _migrate_schema(self) -> None:
        """Añade columnas de identidad si la BD es antigua."""
        logger = get_logger("repository.sqlite")
        try:
            with self._get_connection() as conn:
                columns = {row["name"] for row in conn.execute("PRAGMA table_info(computers)").fetchall()}
                if "device_uuid" not in columns:
                    conn.execute("ALTER TABLE computers ADD COLUMN device_uuid TEXT;")
                if "identity_source" not in columns:
                    conn.execute("ALTER TABLE computers ADD COLUMN identity_source TEXT;")
                if "hardware_ids" not in columns:
                    conn.execute("ALTER TABLE computers ADD COLUMN hardware_ids TEXT;")
                conn.execute("PRAGMA user_version = 3;")
                conn.commit()
        except sqlite3.Error as exc:
            logger.error("No se pudo migrar el esquema de identidad: %s", exc)

    def _row_to_computer(self, row: sqlite3.Row, dimm_list: list[DimmRam], storage_list: list[StorageDrive] | None = None) -> Computer:
        hardware_ids = None
        raw_ids = None
        try:
            raw_ids = row["hardware_ids"]
        except (KeyError, IndexError):
            raw_ids = None
        if raw_ids:
            try:
                import json

                hardware_ids = json.loads(raw_ids)
            except (ValueError, TypeError):
                hardware_ids = None

        device_uuid = None
        identity_source = None
        try:
            device_uuid = row["device_uuid"]
            identity_source = row["identity_source"]
        except (KeyError, IndexError):
            pass

        return Computer(
            device_name=row["device_name"],
            user_name=row["user_name"],
            machine_mac=row["machine_mac"],
            machine_ip=row["machine_ip"],
            mobo_mark=row["mobo_mark"],
            mobo_model=row["mobo_model"],
            cpu_info=row["cpu_info"],
            operative_system=row["operative_system"],
            storage_model=row["storage_model"],
            storage_cap=row["storage_cap"],
            anydesk_id=row["anydesk_id"],
            dimm_list=dimm_list,
            storage_list=storage_list or [],
            device_uuid=device_uuid,
            identity_source=identity_source,
            hardware_ids=hardware_ids,
        )

    def _row_to_storage_drive(self, row: sqlite3.Row) -> StorageDrive:
        letters = [item for item in (row["drive_letters"] or "").split(",") if item]
        return StorageDrive(
            device_id=row["device_id"],
            model=row["model"],
            serial_number=row["serial_number"],
            size_bytes=row["size_bytes"],
            interface_type=row["interface_type"],
            media_type=row["media_type"],
            partitions=row["partitions"],
            drive_letters=letters,
            is_system=bool(row["is_system"]),
        )

    def _row_to_dimm_ram(self, row: sqlite3.Row) -> DimmRam:
        """Convierte una fila de la tabla dimm_ram en un objeto DimmRam."""
        return DimmRam(
            caption=row["caption"],
            manufacturer=row["manufacturer"],
            part_number=row["part_number"],
            model=row["model"],
            tag=row["tag"],
            bank_label=row["bank_label"],
            device_locator=row["device_locator"],
            capacity=row["capacity"],
            speed=row["speed"],
            configured_clock_speed=row["configured_clock_speed"],
            configured_voltage=row["configured_voltage"]
        )

    def _computer_to_tuple(self, computer: Computer) -> tuple:
        """Serializa un Computer a tupla para INSERT/UPDATE."""
        import json

        hardware_ids = (
            json.dumps(computer.hardware_ids, ensure_ascii=False)
            if computer.hardware_ids is not None
            else None
        )
        return (
            computer.machine_mac,
            computer.device_name,
            computer.user_name,
            computer.machine_ip,
            computer.mobo_mark,
            computer.mobo_model,
            computer.cpu_info,
            computer.operative_system,
            computer.storage_model,
            computer.storage_cap,
            computer.anydesk_id,
            computer.device_uuid,
            computer.identity_source,
            hardware_ids,
        )

    def _dimm_ram_to_tuple(self, dimm: DimmRam, machine_mac: str) -> tuple:
        """Serializa un DimmRam a tupla para INSERT (sin id)."""
        return (
            machine_mac,
            dimm.caption,
            dimm.manufacturer,
            dimm.part_number,
            dimm.model,
            dimm.tag,
            dimm.bank_label,
            dimm.device_locator,
            dimm.capacity,
            dimm.speed,
            dimm.configured_clock_speed,
            dimm.configured_voltage
        )

    def _storage_drive_to_tuple(self, drive: StorageDrive, machine_mac: str) -> tuple:
        """Serializa un StorageDrive a tupla para INSERT."""
        return (
            machine_mac,
            drive.device_id,
            drive.model,
            drive.serial_number,
            drive.size_bytes,
            drive.interface_type,
            drive.media_type,
            drive.partitions,
            ",".join(drive.drive_letters),
            1 if drive.is_system else 0,
        )
    # ------------------------------------------------------------------

    def create(self, computer: Computer) -> None:
        """
        Inserta un nuevo registro de computadora con sus módulos RAM.
        Si la MAC ya existe, lanza sqlite3.IntegrityError.
        """
        insert_computer = """
        INSERT INTO computers (
            machine_mac, device_name, user_name, machine_ip,
            mobo_mark, mobo_model, cpu_info, operative_system,
            storage_model, storage_cap, anydesk_id,
            device_uuid, identity_source, hardware_ids
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        insert_dimm = """
        INSERT INTO dimm_ram (
            machine_mac, caption, manufacturer, part_number, model,
            tag, bank_label, device_locator, capacity, speed,
            configured_clock_speed, configured_voltage
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        insert_storage = """
        INSERT INTO storage_drive (
            machine_mac, device_id, model, serial_number, size_bytes,
            interface_type, media_type, partitions, drive_letters, is_system
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        with self._get_connection() as conn:
            conn.execute(insert_computer, self._computer_to_tuple(computer))
            for dimm in computer.dimm_list:
                conn.execute(insert_dimm, self._dimm_ram_to_tuple(dimm, computer.machine_mac))
            for drive in computer.storage_list:
                conn.execute(insert_storage, self._storage_drive_to_tuple(drive, computer.machine_mac))
            conn.commit()

    def read_all(self) -> list[Computer]:
        """Retorna todas las computadoras registradas con sus módulos RAM."""
        computers: list[Computer] = []

        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM computers;")
            rows = cursor.fetchall()

            for row in rows:
                mac = row["machine_mac"]
                dimm_cursor = conn.execute(
                    "SELECT * FROM dimm_ram WHERE machine_mac = ?;", (mac,)
                )
                dimm_rows = dimm_cursor.fetchall()
                dimm_list = [self._row_to_dimm_ram(d) for d in dimm_rows]

                storage_cursor = conn.execute(
                    "SELECT * FROM storage_drive WHERE machine_mac = ?;", (mac,)
                )
                storage_list = [
                    self._row_to_storage_drive(s) for s in storage_cursor.fetchall()
                ]
                computers.append(self._row_to_computer(row, dimm_list, storage_list))

        return computers

    def read_by_mac(self, machine_mac: str) -> Computer | None:
        """Busca una computadora por su dirección MAC."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM computers WHERE machine_mac = ?;", (machine_mac,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            dimm_cursor = conn.execute(
                "SELECT * FROM dimm_ram WHERE machine_mac = ?;", (machine_mac,)
            )
            dimm_list = [self._row_to_dimm_ram(d) for d in dimm_cursor.fetchall()]

            storage_cursor = conn.execute(
                "SELECT * FROM storage_drive WHERE machine_mac = ?;", (machine_mac,)
            )
            storage_list = [self._row_to_storage_drive(s) for s in storage_cursor.fetchall()]
            return self._row_to_computer(row, dimm_list, storage_list)

    def update(self, computer: Computer) -> bool:
        """
        Actualiza una computadora existente (identificada por MAC) y
        reemplaza completamente su lista de módulos RAM.

        Retorna True si se actualizó, False si no existía.
        """
        update_computer = """
        UPDATE computers SET
            device_name = ?,
            user_name = ?,
            machine_ip = ?,
            mobo_mark = ?,
            mobo_model = ?,
            cpu_info = ?,
            operative_system = ?,
            storage_model = ?,
            storage_cap = ?,
            anydesk_id = ?,
            device_uuid = ?,
            identity_source = ?,
            hardware_ids = ?
        WHERE machine_mac = ?;
        """

        with self._get_connection() as conn:
            # Verificar existencia
            cursor = conn.execute(
                "SELECT 1 FROM computers WHERE machine_mac = ?;", (computer.machine_mac,)
            )
            if not cursor.fetchone():
                return False

            # Actualizar datos base
            conn.execute(update_computer, (
                computer.device_name,
                computer.user_name,
                computer.machine_ip,
                computer.mobo_mark,
                computer.mobo_model,
                computer.cpu_info,
                computer.operative_system,
                computer.storage_model,
                computer.storage_cap,
                computer.anydesk_id,
                computer.device_uuid,
                computer.identity_source,
                __import__("json").dumps(computer.hardware_ids, ensure_ascii=False)
                if computer.hardware_ids is not None
                else None,
                computer.machine_mac,
            ))

            # Reemplazar módulos RAM (borrar e insertar)
            conn.execute("DELETE FROM dimm_ram WHERE machine_mac = ?;", (computer.machine_mac,))

            insert_dimm = """
            INSERT INTO dimm_ram (
                machine_mac, caption, manufacturer, part_number, model,
                tag, bank_label, device_locator, capacity, speed,
                configured_clock_speed, configured_voltage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            for dimm in computer.dimm_list:
                conn.execute(insert_dimm, self._dimm_ram_to_tuple(dimm, computer.machine_mac))

            # Reemplazar unidades de almacenamiento (borrar e insertar)
            conn.execute("DELETE FROM storage_drive WHERE machine_mac = ?;", (computer.machine_mac,))

            insert_storage = """
            INSERT INTO storage_drive (
                machine_mac, device_id, model, serial_number, size_bytes,
                interface_type, media_type, partitions, drive_letters, is_system
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            for drive in computer.storage_list:
                conn.execute(insert_storage, self._storage_drive_to_tuple(drive, computer.machine_mac))

            conn.commit()
            return True

    def delete(self, machine_mac: str) -> bool:
        """Elimina una computadora y sus módulos RAM en cascada. Retorna True si existía."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM computers WHERE machine_mac = ?;", (machine_mac,)
            )
            conn.commit()
            return cursor.rowcount > 0

    # ------------------------------------------------------------------
    # Método de compatibilidad con el flujo del repositorio anterior
    # ------------------------------------------------------------------

    def find_and_update_by_mac(self, new_registry: Computer) -> list[Computer]:
        """
        Reproduce el comportamiento del repositorio JSON original:
        - Si la MAC existe: actualiza el registro.
        - Si no existe: lo crea.
        - Retorna la lista completa de computadoras.
        """
        existing = self.read_by_mac(new_registry.machine_mac)

        if existing is None:
            self.create(new_registry)
        else:
            # Verificar cambio en cantidad de módulos RAM
            if len(existing.dimm_list) != len(new_registry.dimm_list):
                PopUpWarning("Precaución", "La cantidad de DIMM RAM es diferente en este registro.")

            self.update(new_registry)

        return self.read_all()

    def close(self) -> None:
        """Cierra cualquier recurso pendiente (SQLite cierra automáticamente con 'with')."""
        pass
