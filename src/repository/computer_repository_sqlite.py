import sqlite3
import os
from typing import Any
from src.models.computer import Computer
from src.models.ram import DimmRam
from src.notifications.popup import PopUp, PopUpError, PopUpWarning, ErrorLogger


class ComputerRepositorySQLite:
    """
    Repositorio de persistencia en SQLite para equipos informáticos.

    Mantiene una relación 1:N entre Computer (tabla principal) y DimmRam (tabla secundaria),
    usando machine_mac como clave primaria/foránea.
    """

    def __init__(self, db_path: str | None = None):
        """
        Inicializa el repositorio SQLite.

        Args:
            db_path: Ruta al archivo .db. Si es None, usa 'localStorage.db' en el directorio actual.
        """
        self.WORKING_PATH = os.getcwd()
        self.DB_NAME = db_path or os.path.join(self.WORKING_PATH, "localStorage.db")
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Retorna una conexión a la base de datos con row_factory configurado."""
        conn = sqlite3.connect(self.DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn

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

        create_index = """
        CREATE INDEX IF NOT EXISTS idx_dimm_mac ON dimm_ram(machine_mac);
        """

        try:
            with self._get_connection() as conn:
                conn.execute(create_computers_table)
                conn.execute(create_dimm_ram_table)
                conn.execute(create_index)
                conn.commit()
        except sqlite3.Error as e:
            PopUpError("Error de Base de Datos", f"No se pudo inicializar SQLite: {e}")
            raise

    # ------------------------------------------------------------------
    # Conversores: Modelo <-> Diccionario <-> SQLite Row
    # ------------------------------------------------------------------

    def _row_to_computer(self, row: sqlite3.Row, dimm_list: list[DimmRam]) -> Computer:
        """Convierte una fila de SQLite + lista de DimmRam en un objeto Computer."""
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
            dimm_list=dimm_list
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
            computer.anydesk_id
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

    # ------------------------------------------------------------------
    # CRUD público
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
            storage_model, storage_cap, anydesk_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        insert_dimm = """
        INSERT INTO dimm_ram (
            machine_mac, caption, manufacturer, part_number, model,
            tag, bank_label, device_locator, capacity, speed,
            configured_clock_speed, configured_voltage
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        with self._get_connection() as conn:
            conn.execute(insert_computer, self._computer_to_tuple(computer))
            for dimm in computer.dimm_list:
                conn.execute(insert_dimm, self._dimm_ram_to_tuple(dimm, computer.machine_mac))
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
                computers.append(self._row_to_computer(row, dimm_list))

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
            return self._row_to_computer(row, dimm_list)

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
            anydesk_id = ?
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
                computer.machine_mac
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
