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

    # Convert a object list of DimmRam to an ordinary List/Dict structure.
    def serialize_dimm_list(self, dimm_list: list[DimmRam]) -> list[dict[str, Any]]:
        dimm_serialized_list = []
        for dimm in dimm_list:
            dimm_serialized = dimm.to_dictionary()
            dimm_serialized_list.append(dimm_serialized)
        return dimm_serialized_list
    
    # Convert a object list of Computer to an ordinary List/Dict structure.
    def serialize_computer_list(self, computer_list: list[Computer]) -> list[dict[str, Any]]:
        updated_data = computer_list
        serialized_computer_list = []
        for computer in updated_data:
            dimm_serialized_list = self.serialize_dimm_list(computer.dimm_list)
            computer_dict = {
                'anydesk_id': computer.anydesk_id,
                'device_name': computer.device_name,
                'user_name': computer.user_name,
                'machine_mac': computer.machine_mac,
                'machine_ip': computer.machine_ip,
                'mobo_mark': computer.mobo_mark,
                'mobo_model': computer.mobo_model,
                'cpu_info': computer.cpu_info,
                'operative_system': computer.operative_system,
                'storage_model': computer.storage_model,
                'storage_cap': computer.storage_cap,
                'dimm_list': dimm_serialized_list
            }
            serialized_computer_list.append(computer_dict)
        return serialized_computer_list
    
    # Write the serialized Computer list into localstorage file.
    def save_data_in_file(self, new_data: list[Computer]) -> None:
        serialized_computer_list = self.serialize_computer_list(new_data)
        try:
            with open(self.STORAGE_FILE, "w") as file:
                json.dump(serialized_computer_list, file, indent=4)
                PopUp("Aviso","¡Ficha guardada correctamente!")
        except OSError as e:
            print(e)

    # Return an updated dimmram list.
    def update_dimm_list(self, current_list: list[DimmRam], new_data_list: list[DimmRam]) -> list[DimmRam]:
        current_dimm_list = current_list
        incoming_dimm_list = new_data_list
        # CHECK this function, if some registry current or incoming changes his lenght of dimms
        # function can raise a ValueError.
        if len(current_dimm_list) != len(incoming_dimm_list):
            PopUp("Precaucion", "La cantidad de dimm RAM es diferente en este registro.")

        # Add function to check if a field need or not the update.
        for dimm, current_dimm in zip(current_dimm_list, incoming_dimm_list):
            dimm.caption = current_dimm.caption
            dimm.manufacturer=current_dimm.manufacturer
            dimm.part_number=current_dimm.part_number
            dimm.model=current_dimm.model
            dimm.tag=current_dimm.tag
            dimm.bank_label=current_dimm.bank_label
            dimm.device_locator=current_dimm.device_locator
            dimm.capacity=current_dimm.capacity
            dimm.speed=current_dimm.speed
            dimm.configured_clock_speed=current_dimm.configured_clock_speed
            dimm.configured_voltage=current_dimm.configured_voltage
            
        return current_dimm_list

    # Return an updated computer object base data. 
    def update_computer_base_info(self, current_data: Computer, new_data: Computer) -> Computer:
        current_data.device_name=new_data.device_name
        current_data.user_name=new_data.user_name
        current_data.machine_ip=new_data.machine_ip
        current_data.mobo_mark=new_data.mobo_mark
        current_data.mobo_model=new_data.mobo_model
        current_data.cpu_info=new_data.cpu_info
        current_data.operative_system=new_data.operative_system
        current_data.storage_model=new_data.storage_model
        current_data.storage_cap=new_data.storage_cap
        current_data.anydesk_id=new_data.anydesk_id
        return current_data

    # Check and update the current data from a Computer List object.
    def find_and_update_by_mac(self, current_records: list[Computer], new_registry: Computer) -> list[Computer]:
        for computer in current_records:
            if computer.machine_mac != new_registry.machine_mac:
                continue

            computer.dimm_list = self.update_dimm_list(computer.dimm_list, new_registry.dimm_list)
            self.update_computer_base_info(computer, new_registry)
            
            return current_records
                
        current_records.append(new_registry)
        return current_records