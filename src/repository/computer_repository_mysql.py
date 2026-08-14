"""
================================================================================
  ComputerRepositoryMySQL – Repositorio de equipos informáticos (MySQL remoto)
================================================================================

  NOTA IMPORTANTE:
  ────────────────
  Esta clase NO crea ni la base de datos ni las tablas. Se asume que el
  esquema ya fue creado previamente mediante el script SQL proporcionado
  (schema.sql) o por el administrador de la base de datos.

  Tablas requeridas:
    • computers  (machine_mac VARCHAR(17) PRIMARY KEY, ...)
    • dimm_ram   (id INT AUTO_INCREMENT PRIMARY KEY, machine_mac FK, ...)

  Asegúrate de ejecutar el script schema.sql antes de usar esta clase.

================================================================================

CONFIGURACIÓN MEDIANTE VARIABLES DE ENTORNO (.env)
--------------------------------------------------
El archivo .env debe ubicarse en la raíz del proyecto y contener:

  # Obligatorias
  MYSQL_HOST=mi-servidor-mysql.ejemplo.com
  MYSQL_PORT=3306
  MYSQL_USER=mi_usuario
  MYSQL_PASSWORD=mi_contraseña_segura
  MYSQL_DATABASE=inventario_db

  # Opcionales
  MYSQL_POOL_NAME=computer_pool
  MYSQL_POOL_SIZE=5
  MYSQL_CHARSET=utf8mb4
  MYSQL_SSL_CA=/ruta/ca.pem
  MYSQL_SSL_VERIFY_CERT=true

================================================================================
"""

import os
from typing import Any
from dotenv import load_dotenv

# Cargar variables de entorno desde .env antes de cualquier otra operación
load_dotenv()

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    from mysql.connector.pooling import MySQLConnectionPool
except ImportError:
    raise ImportError(
        "El paquete 'mysql-connector-python' es requerido. "
        "Instálalo con: pip install mysql-connector-python"
    )

from src.models.computer import Computer
from src.models.ram import DimmRam
from src.notifications.popup import PopUp, PopUpError, PopUpWarning, ErrorLogger


class ComputerRepositoryMySQL:
    """
    Repositorio de persistencia en MySQL remoto para equipos informáticos.

    Utiliza un pool de conexiones para manejar múltiples solicitudes de forma
    eficiente. Mantiene relación 1:N entre computers y dimm_ram mediante
    machine_mac como clave primaria/foránea.

    PRECONDICIÓN: Las tablas 'computers' y 'dimm_ram' deben existir en la
    base de datos antes de instanciar esta clase.
    """

    def __init__(self):
        """
        Inicializa el pool de conexiones MySQL leyendo la configuración
        desde variables de entorno (vía python-dotenv).

        Raises:
            EnvironmentError: Si faltan variables de entorno obligatorias.
            MySQLError: Si no se puede establecer el pool de conexiones.
        """
        self._load_config()
        self._init_pool()

    # ------------------------------------------------------------------
    # Configuración
    # ------------------------------------------------------------------

    def _load_config(self) -> None:
        """Lee y valida las variables de entorno necesarias."""
        required = ["MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE"]
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise EnvironmentError(
                f"Faltan variables de entorno obligatorias: {', '.join(missing)}"
            )

        self._config = {
            "host": os.getenv("MYSQL_HOST"),
            "port": int(os.getenv("MYSQL_PORT", "3306")),
            "user": os.getenv("MYSQL_USER"),
            "password": os.getenv("MYSQL_PASSWORD"),
            "database": os.getenv("MYSQL_DATABASE"),
            "charset": os.getenv("MYSQL_CHARSET", "utf8mb4"),
            "collation": "utf8mb4_general_ci",
            "autocommit": False,
            "raise_on_warnings": True,
        }

        # Configuración SSL opcional
        ssl_ca = os.getenv("MYSQL_SSL_CA")
        if ssl_ca:
            self._config["ssl_ca"] = ssl_ca
            self._config["ssl_verify_cert"] = (
                os.getenv("MYSQL_SSL_VERIFY_CERT", "false").lower() == "true"
            )

        self._pool_name = os.getenv("MYSQL_POOL_NAME", "computer_pool")
        self._pool_size = int(os.getenv("MYSQL_POOL_SIZE", "5"))

    def _init_pool(self) -> None:
        """Crea el pool de conexiones a MySQL."""
        try:
            self._pool = MySQLConnectionPool(
                pool_name=self._pool_name,
                pool_size=self._pool_size,
                **self._config
            )
        except MySQLError as e:
            PopUpError("Error de Conexión MySQL", f"No se pudo crear el pool: {e}")
            raise

    def _get_connection(self):
        """Obtiene una conexión del pool."""
        return self._pool.get_connection()

    # ------------------------------------------------------------------
    # Conversores
    # ------------------------------------------------------------------

    def _row_to_computer(self, row: tuple, dimm_list: list[DimmRam]) -> Computer:
        """Convierte una tupla de resultado MySQL en un objeto Computer."""
        # row: (machine_mac, device_name, user_name, machine_ip, mobo_mark,
        #       mobo_model, cpu_info, operative_system, storage_model,
        #       storage_cap, anydesk_id, updated_at, created_at)
        return Computer(
            device_name=row[1],
            user_name=row[2],
            machine_mac=row[0],
            machine_ip=row[3],
            mobo_mark=row[4],
            mobo_model=row[5],
            cpu_info=row[6],
            operative_system=row[7],
            storage_model=row[8],
            storage_cap=row[9],
            anydesk_id=row[10],
            dimm_list=dimm_list
        )

    def _row_to_dimm_ram(self, row: tuple) -> DimmRam:
        """Convierte una tupla de dimm_ram en un objeto DimmRam."""
        # row: (id, machine_mac, caption, manufacturer, part_number, model,
        #       tag, bank_label, device_locator, capacity, speed,
        #       configured_clock_speed, configured_voltage)
        return DimmRam(
            caption=row[2],
            manufacturer=row[3],
            part_number=row[4],
            model=row[5],
            tag=row[6],
            bank_label=row[7],
            device_locator=row[8],
            capacity=row[9],
            speed=row[10],
            configured_clock_speed=row[11],
            configured_voltage=row[12]
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
        Si la MAC ya existe, lanza mysql.connector.IntegrityError.
        """
        insert_computer = """
        INSERT INTO computers (
            machine_mac, device_name, user_name, machine_ip,
            mobo_mark, mobo_model, cpu_info, operative_system,
            storage_model, storage_cap, anydesk_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        insert_dimm = """
        INSERT INTO dimm_ram (
            machine_mac, caption, manufacturer, part_number, model,
            tag, bank_label, device_locator, capacity, speed,
            configured_clock_speed, configured_voltage
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(insert_computer, self._computer_to_tuple(computer))
            for dimm in computer.dimm_list:
                cursor.execute(insert_dimm, self._dimm_ram_to_tuple(dimm, computer.machine_mac))
            conn.commit()
        except MySQLError:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def read_all(self) -> list[Computer]:
        """Retorna todas las computadoras registradas con sus módulos RAM."""
        computers: list[Computer] = []
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM computers;")
            rows = cursor.fetchall()

            for row in rows:
                mac = row[0]
                cursor.execute("SELECT * FROM dimm_ram WHERE machine_mac = %s;", (mac,))
                dimm_rows = cursor.fetchall()
                dimm_list = [self._row_to_dimm_ram(d) for d in dimm_rows]
                computers.append(self._row_to_computer(row, dimm_list))

            return computers
        except MySQLError as e:
            PopUpError("Error de Lectura MySQL", f"No se pudieron leer los registros: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def read_by_mac(self, machine_mac: str) -> Computer | None:
        """Busca una computadora por su dirección MAC."""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM computers WHERE machine_mac = %s;", (machine_mac,))
            row = cursor.fetchone()
            if not row:
                return None

            cursor.execute("SELECT * FROM dimm_ram WHERE machine_mac = %s;", (machine_mac,))
            dimm_list = [self._row_to_dimm_ram(d) for d in cursor.fetchall()]
            return self._row_to_computer(row, dimm_list)
        except MySQLError as e:
            PopUpError("Error de Lectura MySQL", f"No se pudo buscar por MAC: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def update(self, computer: Computer) -> bool:
        """
        Actualiza una computadora existente (identificada por MAC) y
        reemplaza completamente su lista de módulos RAM.

        Retorna True si se actualizó, False si no existía.
        """
        update_computer = """
        UPDATE computers SET
            device_name = %s,
            user_name = %s,
            machine_ip = %s,
            mobo_mark = %s,
            mobo_model = %s,
            cpu_info = %s,
            operative_system = %s,
            storage_model = %s,
            storage_cap = %s,
            anydesk_id = %s
        WHERE machine_mac = %s;
        """

        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Verificar existencia
            cursor.execute("SELECT 1 FROM computers WHERE machine_mac = %s;", (computer.machine_mac,))
            if not cursor.fetchone():
                return False

            # Actualizar datos base
            cursor.execute(update_computer, (
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
            cursor.execute("DELETE FROM dimm_ram WHERE machine_mac = %s;", (computer.machine_mac,))

            insert_dimm = """
            INSERT INTO dimm_ram (
                machine_mac, caption, manufacturer, part_number, model,
                tag, bank_label, device_locator, capacity, speed,
                configured_clock_speed, configured_voltage
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            for dimm in computer.dimm_list:
                cursor.execute(insert_dimm, self._dimm_ram_to_tuple(dimm, computer.machine_mac))

            conn.commit()
            return True
        except MySQLError:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def delete(self, machine_mac: str) -> bool:
        """Elimina una computadora y sus módulos RAM en cascada. Retorna True si existía."""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM computers WHERE machine_mac = %s;", (machine_mac,))
            conn.commit()
            return cursor.rowcount > 0
        except MySQLError as e:
            PopUpError("Error de Eliminación MySQL", f"No se pudo eliminar: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # ------------------------------------------------------------------
    # Método de compatibilidad con el flujo del repositorio original
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
        """Cierra el pool de conexiones de MySQL."""
        if hasattr(self, "_pool") and self._pool:
            self._pool._remove_connections()
