import os
import json

from src.pop_up import PopUp
from socket import gethostname

WORKING_PATH = os.getcwd()
COMPUTER_NAME = gethostname()
FILE_NAME = "localStorage.json"
STORAGE_FILE = os.path.join(WORKING_PATH, FILE_NAME)

class Writer:    
    def __init__(self):
        self.check_local_storage()

    def check_local_storage(self):
        try:
            if not os.path.exists(STORAGE_FILE):
                with open(STORAGE_FILE, "w") as file:
                    json.dump([], file)
        except OSError as e:
            pass
        
    def load_local_storage(self) -> list[dict[str, str]]:
        data = []
        try:
            with open(STORAGE_FILE, "r") as file:
                data = json.load(file)
        except OSError as e:
            print(f"Error alcanzado. {e}")
        except json.JSONDecodeError as e:
            data = []
        return data
    
    # Give the updated data for write.
    def save_data_in_file(self, new_data):
        try:
            with open(STORAGE_FILE, "w") as file:
                json.dump(new_data, file, indent=4)
        except OSError as e:
            print(e)
    
    def check_fields_and_update(self, old_data, new_data):
        to_update = old_data.copy()
        modified = False
        for key in old_data:
            old_value = old_data.get(key)
            new_value = new_data.get(key)
            if old_value !=  new_value:
                to_update[key] = new_data[key]
                modified = True
        return to_update if modified else None

    def find_and_update_by_mac(self, new_registry):
        current_data = self.load_local_storage()
        for index, registry in enumerate(current_data):
            if new_registry['machine_mac'] == registry['machine_mac']:
                changes = self.check_fields_and_update(registry, new_registry)
                if changes:
                    current_data[index] = changes
                    self.save_data_in_file(current_data)
                break
        current_data.append(new_registry)
        self.save_data_in_file(current_data)
        PopUp("Estado", "Ficha guardada correctamente.")