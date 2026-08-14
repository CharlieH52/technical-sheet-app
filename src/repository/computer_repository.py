"""
================================================================================
  computer_repository.py – Repositorio de persistencia local (JSON)
================================================================================

  Propósito:
  ─────────
  Gestiona el almacenamiento local de registros de equipos informáticos
  en un archivo JSON plano (localStorage.json). Sirve como capa de
  persistencia legacy antes de la migración a bases de datos relacionales.

  Funcionalidad principal:
  ───────────────────────
  • Crear/verificar el archivo de almacenamiento JSON.
  • Leer y deserializar registros en objetos Computer y DimmRam.
  • Serializar objetos a diccionarios para guardar en JSON.
  • Buscar por dirección MAC y actualizar/agregar registros.

  Sistema de notificaciones:
  ──────────────────────────
  Utiliza PopUp, PopUpWarning, PopUpError y ErrorLogger del módulo
  src.notifications.popup para informar al usuario y registrar errores
  extensos en archivos .log.

  Notas:
  ──────
  • La dirección MAC (machine_mac) se utiliza como identificador único.
  • Si la cantidad de módulos RAM cambia entre lecturas, se muestra una
    advertencia al usuario mediante PopUpWarning.
  • Los errores de permisos o lectura/escritura se manejan con PopUpError
    y se registran en error_logs.txt si el mensaje supera 100 caracteres.

================================================================================
"""

import os
import json
from typing import Any
from socket import gethostname

from src.notifications.popup import PopUp, PopUpError, PopUpWarning, ErrorLogger
from src.models.computer import Computer
from src.models.ram import DimmRam


class ComputerRepositoryLocal:
    """
    Repositorio de persistencia local en formato JSON.

    Gestiona un archivo localStorage.json en el directorio de trabajo actual,
    donde almacena una lista de equipos informáticos con sus especificaciones
    de hardware, red, sistema operativo y módulos de memoria RAM.

    Atributos:
        WORKING_PATH: Ruta absoluta del directorio de ejecución.
        COMPUTER_NAME: Nombre del equipo obtenido del sistema operativo.
        FILE_NAME: Nombre fijo del archivo de almacenamiento.
        STORAGE_FILE: Ruta completa al archivo JSON.
    """

    def __init__(self):
        """
        Inicializa el repositorio configurando rutas y verificando
        la existencia del archivo de almacenamiento JSON.
        """
        self.WORKING_PATH = os.getcwd()
        self.COMPUTER_NAME = gethostname()
        self.FILE_NAME = "localStorage.json"
        self.STORAGE_FILE = os.path.join(self.WORKING_PATH, self.FILE_NAME)
        self.check_local_storage()

    # ------------------------------------------------------------------
    # Gestión del archivo de almacenamiento
    # ------------------------------------------------------------------

    def check_local_storage(self) -> None:
        """
        Verifica si el archivo JSON de almacenamiento local existe.
        Si no existe, lo crea con una lista vacía [] para permitir
        que json.load() funcione correctamente en lecturas posteriores.

        Maneja PermissionError mostrando una notificación al usuario
        y registrando el error en el archivo de log si es extenso.
        """
        try:
            if not os.path.exists(self.STORAGE_FILE):
                with open(self.STORAGE_FILE, "w", encoding="utf-8") as file:
                    # Los corchetes son esenciales para que json.load()
                    # interprete correctamente el contenido como una lista vacía.
                    json.dump([], file)
        except PermissionError as e:
            error_msg = (
                f"No se pudo crear el archivo de almacenamiento local "
                f"'{self.STORAGE_FILE}'. Verifique los permisos de escritura "
                f"en el directorio '{self.WORKING_PATH}'. Detalle: {e}"
            )
            PopUpError("Error de Permisos", error_msg)

    def load_local_storage(self) -> list[dict[str, Any]]:
        """
        Lee el archivo JSON de almacenamiento local y devuelve su contenido
        como una lista de diccionarios.

        Maneja errores de lectura (OSError) y archivos corruptos (JSONDecodeError)
        devolviendo una lista vacía y notificando al usuario.

        Returns:
            Lista de diccionarios con los registros de computadoras.
            Devuelve lista vacía si ocurre algún error.
        """
        current_data: list[dict[str, Any]] = []
        try:
            with open(self.STORAGE_FILE, "r", encoding="utf-8") as file:
                current_data = json.load(file)
        except OSError as e:
            error_msg = (
                f"Error al leer el archivo de almacenamiento local "
                f"'{self.STORAGE_FILE}'. Es posible que el archivo esté "
                f"bloqueado por otro proceso o que el disco esté lleno. "
                f"Detalle: {e}"
            )
            PopUpError("Error de Lectura", error_msg)
        except json.JSONDecodeError as e:
            error_msg = (
                f"El archivo de almacenamiento '{self.STORAGE_FILE}' está "
                f"corrupto o no contiene un JSON válido. Se inicializará "
                f"una lista vacía. Detalle: {e}"
            )
            PopUpWarning("Archivo Corrupto", error_msg)
            current_data = []
        return current_data

    # ------------------------------------------------------------------
    # Fábricas de objetos (deserialización)
    # ------------------------------------------------------------------

    def create_computer_object(
        self,
        computer_data: dict[str, Any],
        obj_dimm_list: list[DimmRam]
    ) -> Computer:
        """
        Construye un objeto Computer a partir de un diccionario y una lista
        de objetos DimmRam previamente deserializados.

        Args:
            computer_data: Diccionario con los campos del equipo.
            obj_dimm_list: Lista de objetos DimmRam asociados al equipo.

        Returns:
            Instancia de Computer con todos sus atributos poblados.
        """
        return Computer(
            device_name=computer_data.get("device_name"),
            user_name=computer_data.get("user_name"),
            machine_mac=computer_data.get("machine_mac"),
            machine_ip=computer_data.get("machine_ip"),
            mobo_mark=computer_data.get("mobo_mark"),
            mobo_model=computer_data.get("mobo_model"),
            cpu_info=computer_data.get("cpu_info"),
            operative_system=computer_data.get("operative_system"),
            storage_model=computer_data.get("storage_model"),
            storage_cap=computer_data.get("storage_cap"),
            anydesk_id=computer_data.get("anydesk_id"),
            dimm_list=obj_dimm_list
        )

    def create_dimm_ram_list(self, dimm_data: list[dict[str, Any]]) -> list[DimmRam]:
        """
        Construye una lista de objetos DimmRam a partir de una lista de
        diccionarios provenientes del JSON.

        Nota sobre las claves:
            El JSON almacena las claves en formato PascalCase (Caption,
            Manufacturer, PartNumber, etc.) porque provienen originalmente
            de consultas WMI en Windows.

        Args:
            dimm_data: Lista de diccionarios con datos de módulos RAM.

        Returns:
            Lista de instancias DimmRam.
        """
        obj_dimm_list: list[DimmRam] = []
        for dimm in dimm_data:
            dimm_object = DimmRam(
                caption=dimm.get("Caption"),
                manufacturer=dimm.get("Manufacturer"),
                part_number=dimm.get("PartNumber"),
                model=dimm.get("Model"),
                tag=dimm.get("Tag"),
                bank_label=dimm.get("BankLabel"),
                device_locator=dimm.get("DeviceLocator"),
                capacity=dimm.get("Capacity"),
                speed=dimm.get("Speed"),
                configured_clock_speed=dimm.get("ConfiguredClockSpeed"),
                configured_voltage=dimm.get("ConfiguredVoltage")
            )
            obj_dimm_list.append(dimm_object)
        return obj_dimm_list

    def create_computer_list(self) -> list[Computer]:
        """
        Carga el archivo JSON completo y convierte cada registro en un
        objeto Computer con su lista de módulos DimmRam asociados.

        Returns:
            Lista de objetos Computer representando todos los equipos
            almacenados en el archivo local.
        """
        obj_computer_list: list[Computer] = []
        current_data = self.load_local_storage()

        for computer in current_data:
            dimm_ram_list = computer.get("dimm_list")
            obj_dimm_list = self.create_dimm_ram_list(dimm_ram_list)
            computer_object = self.create_computer_object(computer, obj_dimm_list)
            obj_computer_list.append(computer_object)

        return obj_computer_list

    # ------------------------------------------------------------------
    # Serialización (objetos → diccionarios)
    # ------------------------------------------------------------------

    def serialize_dimm_list(self, dimm_list: list[DimmRam]) -> list[dict[str, Any]]:
        """
        Convierte una lista de objetos DimmRam en una lista de diccionarios
        serializables a JSON.

        Args:
            dimm_list: Lista de instancias DimmRam.

        Returns:
            Lista de diccionarios con las claves en formato PascalCase.
        """
        dimm_serialized_list: list[dict[str, Any]] = []
        for dimm in dimm_list:
            dimm_serialized = dimm.to_dictionary()
            dimm_serialized_list.append(dimm_serialized)
        return dimm_serialized_list

    def serialize_computer_list(self, computer_list: list[Computer]) -> list[dict[str, Any]]:
        """
        Convierte una lista de objetos Computer en una lista de diccionarios
        listos para ser guardados en el archivo JSON.

        Cada objeto Computer se descompone en sus campos base más la lista
        de módulos RAM serializados recursivamente.

        Args:
            computer_list: Lista de instancias Computer.

        Returns:
            Lista de diccionarios con la estructura esperada por el JSON.
        """
        serialized_computer_list: list[dict[str, Any]] = []
        for computer in computer_list:
            dimm_serialized_list = self.serialize_dimm_list(computer.dimm_list)
            computer_dict = {
                "anydesk_id": computer.anydesk_id,
                "device_name": computer.device_name,
                "user_name": computer.user_name,
                "machine_mac": computer.machine_mac,
                "machine_ip": computer.machine_ip,
                "mobo_mark": computer.mobo_mark,
                "mobo_model": computer.mobo_model,
                "cpu_info": computer.cpu_info,
                "operative_system": computer.operative_system,
                "storage_model": computer.storage_model,
                "storage_cap": computer.storage_cap,
                "dimm_list": dimm_serialized_list
            }
            serialized_computer_list.append(computer_dict)
        return serialized_computer_list

    # ------------------------------------------------------------------
    # Persistencia en archivo
    # ------------------------------------------------------------------

    def save_data_in_file(self, new_data: list[Computer]) -> None:
        """
        Serializa la lista de objetos Computer y la escribe en el archivo
        localStorage.json con formato indentado.

        Maneja errores de escritura (OSError) notificando al usuario
        y registrando el error en el log si el mensaje es extenso.

        Args:
            new_data: Lista de objetos Computer a persistir.
        """
        serialized_computer_list = self.serialize_computer_list(new_data)
        try:
            with open(self.STORAGE_FILE, "w", encoding="utf-8") as file:
                json.dump(serialized_computer_list, file, indent=4)
        except OSError as e:
            error_msg = (
                f"Error al guardar los datos en '{self.STORAGE_FILE}'. "
                f"Verifique que el disco no esté lleno y que la aplicación "
                f"tenga permisos de escritura. Detalle: {e}"
            )
            PopUpError("Error de Escritura", error_msg)

    # ------------------------------------------------------------------
    # Actualización de registros
    # ------------------------------------------------------------------

    def update_dimm_list(
        self,
        current_list: list[DimmRam],
        new_data_list: list[DimmRam]
    ) -> list[DimmRam]:
        """
        Actualiza los atributos de los módulos RAM existentes con los datos
        de los módulos nuevos.

        Advertencia:
            Si la cantidad de módulos RAM difiere entre el registro actual
            y el nuevo, se muestra un PopUpWarning al usuario. Esto puede
            indicar un cambio de hardware (upgrade de memoria o módulo
            defectuoso no detectado).

        Nota:
            Los módulos se actualizan posición por posición mediante zip(),
            por lo que si las listas tienen longitudes diferentes, los
            módulos sobrantes no se procesan.

        Args:
            current_list: Lista actual de módulos DimmRam del registro existente.
            new_data_list: Lista nueva de módulos DimmRam del escaneo actual.

        Returns:
            Lista actualizada de objetos DimmRam.
        """
        current_dimm_list = current_list
        incoming_dimm_list = new_data_list

        # Verificar si la cantidad de módulos RAM cambió entre lecturas.
        # Esto puede indicar un upgrade de memoria o un módulo defectuoso.
        if len(current_dimm_list) != len(incoming_dimm_list):
            PopUpWarning(
                "Precaución",
                "La cantidad de módulos DIMM RAM es diferente en este registro. "
                "Esto puede indicar un cambio de hardware desde la última lectura."
            )

        # Actualizar campo por campo cada módulo RAM existente.
        # Se usa zip() por posición; si las longitudes difieren,
        # los módulos sobrantes se ignoran.
        for dimm, current_dimm in zip(current_dimm_list, incoming_dimm_list):
            dimm.caption = current_dimm.caption
            dimm.manufacturer = current_dimm.manufacturer
            dimm.part_number = current_dimm.part_number
            dimm.model = current_dimm.model
            dimm.tag = current_dimm.tag
            dimm.bank_label = current_dimm.bank_label
            dimm.device_locator = current_dimm.device_locator
            dimm.capacity = current_dimm.capacity
            dimm.speed = current_dimm.speed
            dimm.configured_clock_speed = current_dimm.configured_clock_speed
            dimm.configured_voltage = current_dimm.configured_voltage

        return current_dimm_list

    def update_computer_base_info(
        self,
        current_data: Computer,
        new_data: Computer
    ) -> Computer:
        """
        Actualiza los campos base de un objeto Computer existente con los
        datos de un nuevo escaneo.

        Nota:
            La dirección MAC (machine_mac) NO se actualiza porque es el
            identificador único del equipo y no debe cambiar.

        Args:
            current_data: Objeto Computer existente a modificar.
            new_data: Objeto Computer con los datos más recientes.

        Returns:
            El mismo objeto current_data modificado (mutación in-place).
        """
        current_data.device_name = new_data.device_name
        current_data.user_name = new_data.user_name
        current_data.machine_ip = new_data.machine_ip
        current_data.mobo_mark = new_data.mobo_mark
        current_data.mobo_model = new_data.mobo_model
        current_data.cpu_info = new_data.cpu_info
        current_data.operative_system = new_data.operative_system
        current_data.storage_model = new_data.storage_model
        current_data.storage_cap = new_data.storage_cap
        current_data.anydesk_id = new_data.anydesk_id
        return current_data

    # ------------------------------------------------------------------
    # Búsqueda y sincronización principal
    # ------------------------------------------------------------------

    def find_and_update_by_mac(
        self,
        current_records: list[Computer],
        new_registry: Computer
    ) -> list[Computer]:
        """
        Busca un registro existente por dirección MAC y lo actualiza;
        si no existe, lo agrega como nuevo.

        Este es el método principal de sincronización del repositorio.
        Recorre la lista de registros actuales comparando la MAC del nuevo
        escaneo. Si encuentra coincidencia, actualiza los datos base y
        los módulos RAM. Si no encuentra coincidencia, agrega el nuevo
        registro al final de la lista.

        Args:
            current_records: Lista actual de objetos Computer cargada del JSON.
            new_registry: Objeto Computer con los datos del escaneo actual.

        Returns:
            Lista actualizada de objetos Computer lista para ser guardada.
        """
        for computer in current_records:
            if computer.machine_mac != new_registry.machine_mac:
                continue

            # MAC coincidente encontrada: actualizar registro existente.
            computer.dimm_list = self.update_dimm_list(
                computer.dimm_list,
                new_registry.dimm_list
            )
            self.update_computer_base_info(computer, new_registry)
            return current_records

        # No se encontró coincidencia: agregar nuevo registro.
        current_records.append(new_registry)
        return current_records
