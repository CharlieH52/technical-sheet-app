"""
================================================================================
  main.py – Script principal de inventario de equipos informáticos
================================================================================

FLUJO DE EJECUCIÓN:
  1. Recolecta información del equipo actual (hardware, red, SO, usuario, AnyDesk).
  2. Construye un objeto Computer con todos los datos.
  3. Persiste el registro en la base de datos configurada:
     a) JSON local (legacy)  → ComputerRepositoryLocal
     b) SQLite local         → ComputerRepositorySQLite
     c) MySQL remoto         → ComputerRepositoryMySQL (condicional)

CONFIGURACIÓN MEDIANTE VARIABLES DE ENTORNO (.env)
--------------------------------------------------
  # Obligatorias para MySQL remoto (si se habilita)
  MYSQL_HOST=mi-servidor-mysql.ejemplo.com
  MYSQL_PORT=3306
  MYSQL_USER=mi_usuario
  MYSQL_PASSWORD=mi_contraseña_segura
  MYSQL_DATABASE=inventario_db

  # Opcionales
  MYSQL_POOL_SIZE=5
  MYSQL_SSL_CA=/ruta/ca.pem

  # Variable DEDICADA para activar/desactivar envío remoto a MySQL
  USE_MYSQL_REMOTE=false    # "true"  → envía datos al servidor MySQL remoto
                            # "false" → solo usa SQLite local (default)

================================================================================
  NOTA IMPORTANTE SOBRE MIGRACIÓN DE PERSISTENCIA
================================================================================

Para dejar de trabajar "en crudo" con JSON y migrar completamente a bases
relacionales, realiza los siguientes pasos:

  1. Comenta o elimina las líneas marcadas con [LEGACY-JSON] en este archivo.
  2. Asegúrate de que ComputerRepositorySQLite esté activo (ya lo está por defecto).
  3. (Opcional) Si deseas sincronización remota, define USE_MYSQL_REMOTE=true
     y configura las variables MYSQL_* correspondientes.
  4. Elimina el archivo localStorage.json cuando ya no lo necesites.

Ejemplo de .env mínimo (solo local):
  USE_MYSQL_REMOTE=false

Ejemplo de .env con sincronización remota:
  USE_MYSQL_REMOTE=true
  MYSQL_HOST=192.168.1.50
  MYSQL_PORT=3306
  MYSQL_USER=admin
  MYSQL_PASSWORD=SuperSecret123!
  MYSQL_DATABASE=computers_inventory
================================================================================
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

from src.modules.mod_anydesk import AnyDeskInfo
from src.modules.mod_hardware import HardwareInfo
from src.modules.mod_network import NetworkInfo
from src.modules.mod_os import OperativeSystem
from src.modules.mod_user import UserInformation

# ──────────────────────────────────────────────────────────────────────────────
# [LEGACY-JSON] Repositorio en crudo (JSON plano).
# Comenta las siguientes 2 líneas para dejar de usar persistencia en archivo JSON.
# ──────────────────────────────────────────────────────────────────────────────
from src.repository.computer_repository import ComputerRepositoryLocal

from src.repository.computer_repository_sqlite import ComputerRepositorySQLite
from src.repository.computer_repository_mysql import ComputerRepositoryMySQL
from src.computer_builder import ComputerBuilder
from src.notifications.popup import PopUp


def main():
    # ------------------------------------------------------------------
    # PASO 1: Cargar registros existentes desde JSON (legacy)
    # ------------------------------------------------------------------
    # [LEGACY-JSON] Este bloque lee el archivo localStorage.json.
    # Comenta estas líneas si ya no usas JSON.
    crl = ComputerRepositoryLocal()
    current_computer_list = crl.create_computer_list()

    # ------------------------------------------------------------------
    # PASO 2: Recolectar información del equipo actual
    # ------------------------------------------------------------------
    # Se instancian los proveedores de datos y se construye el objeto Computer.
    new_computer = ComputerBuilder(
        anydesk_provider=AnyDeskInfo(),
        user_provider=UserInformation(),
        hardware_provider=HardwareInfo(),
        system_provider=OperativeSystem(),
        network_provider=NetworkInfo()
    ).create_computer()

    # ------------------------------------------------------------------
    # PASO 3: Actualizar/insertar en JSON local (legacy)
    # ------------------------------------------------------------------
    # [LEGACY-JSON] Este bloque guarda en localStorage.json.
    # Comenta estas líneas si ya no usas JSON.
    updated_computer_list = crl.find_and_update_by_mac(current_computer_list, new_computer)
    crl.save_data_in_file(updated_computer_list)

    # ------------------------------------------------------------------
    # PASO 4: Persistir en SQLite (base de datos local recomendada)
    # ------------------------------------------------------------------
    # SQLite se ejecuta siempre como persistencia local principal.
    sql_repo = ComputerRepositorySQLite(None)
    sql_repo.find_and_update_by_mac(new_computer)

    # ------------------------------------------------------------------
    # PASO 5: Evaluar si se debe enviar a MySQL remoto
    # ------------------------------------------------------------------
    # La variable USE_MYSQL_REMOTE controla si se sincroniza con el servidor remoto.
    # Si es "true", se instancia ComputerRepositoryMySQL y se envían los datos.
    # Si es "false" (o cualquier otro valor), se omite completamente MySQL.
    use_mysql = os.getenv("USE_MYSQL_REMOTE", "false").lower().strip()

    if use_mysql == "true":
        mysql_repo = ComputerRepositoryMySQL()
        mysql_repo.find_and_update_by_mac(new_computer)
        mysql_repo.close()

    # ------------------------------------------------------------------
    # PASO 6: Notificación final al usuario
    # ------------------------------------------------------------------
    PopUp("Aviso", "¡Ficha guardada correctamente!")


if __name__ == "__main__":
    main()
