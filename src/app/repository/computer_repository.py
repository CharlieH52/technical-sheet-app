import os
import json
from app.notifications.popup import PopUp
from app.models.computer import Computer
from app.models.ram import DimmRam
from socket import gethostname
from typing import Any

class ComputerRepositoryLocal:    
    def __init__(self):
        self.WORKING_PATH = os.getcwd()
        self.COMPUTER_NAME = gethostname()
        self.FILE_NAME = "localStorage.json"
        self.STORAGE_FILE = os.path.join(self.WORKING_PATH, self.FILE_NAME)
        self.check_local_storage()

    # Verify if JSON local storage exists.
    def check_local_storage(self) -> None:
        try:
            if not os.path.exists(self.STORAGE_FILE):
                with open(self.STORAGE_FILE, "w") as file:
                    json.dump([], file) # These brackets are important for the loads method.
        except PermissionError as e:
            print(e)
        
    # Read local storage file and returns a non serialized data structure.
    def load_local_storage(self) -> list[dict[str, Any]]:
        current_data = []
        try:
            with open(self.STORAGE_FILE, "r") as file:
                current_data = json.load(file)
        except OSError as e:
            print(f"Error alcanzado. {e}")
        except json.JSONDecodeError as e:
            current_data = []
        return current_data
    
    # Return a Computer object.
    def create_computer_object(self, computer_data: dict[str, Any], obj_dimm_list: list[DimmRam]) -> Computer:
        computer_object = Computer(
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
        return computer_object

    # Return a Dimm Memory object list.
    def create_dimm_ram_list(self, dimm_data: list[dict[str, Any]]) -> list[DimmRam]:
        obj_dimm_list = []
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

    # Return a Computer object list.
    def create_computer_list(self) -> list[Computer]:
        obj_computer_list = []
        current_data = self.load_local_storage()
        for computer in current_data:
            dimm_ram_list = computer.get("dimm_list")
            obj_dimm_list = self.create_dimm_ram_list(dimm_ram_list)
            computer_object = self.create_computer_object(computer, obj_dimm_list)
            obj_computer_list.append(computer_object)
        return obj_computer_list

    # Write the Computer list in the localstorage file.
    def save_data_in_file(self, new_data: list[Computer]) -> None:
        try:
            with open(self.STORAGE_FILE, "w") as file:
                json.dump(new_data, file, indent=4)
        except OSError as e:
            print(e)
    
    # def check_fields_and_update(self, old_data, new_data):
    #     to_update = old_data.copy()
    #     modified = False
    #     for key in old_data:
    #         old_value = old_data.get(key)
    #         new_value = new_data.get(key)
    #         if old_value !=  new_value:
    #             to_update[key] = new_data[key]
    #             modified = True
    #     return to_update if modified else None

    def find_and_update_by_mac(self, new_registry):
        current_data = self.load_local_storage()
        for index, registry in enumerate(current_data):
            if new_registry['machine_mac'] == registry['machine_mac']:
                # changes = self.check_fields_and_update(registry, new_registry)
                if changes:
                    current_data[index] = changes
                    self.save_data_in_file(current_data)
                    PopUp("Estado", "Registro actualizado correctamente.")
                return
        current_data.append(new_registry)
        self.save_data_in_file(current_data)
        PopUp("Estado", "Ficha guardada correctamente.")
