import os
import json

from socket import gethostname

WORKING_PATH = os.getcwd()
COMPUTER_NAME = gethostname()
FILE_NAME = 'localStorage.json'
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
        
    def load_local_storage(self):
        try:
            with open(STORAGE_FILE, "r") as file:
                data = json.load(file)
                return data
        except OSError as e:
            pass

        except PermissionError as e:
            pass
    
    def mac_id_checker(self, new_registry):
        outdate_file = self.load_local_storage()
        existing = next((registry for registry in outdate_file if  new_registry['machine_mac'] == registry['machine_mac']), None)
        if existing:
            for key, registry in new_registry.items():
                old_value = existing.get(key)
                new_value = new_registry.get(key)
                if old_value !=  new_value:
                    existing[key] = new_registry[key]
            return existing
    # 1. Bring the current data and the incomming data.
    # 2. Compare both MAC Address.
    # 3. If the address are equals, compare the data field by field.
    # 3.1 If the address isnot in the current data, just add the new registry into the list with append.   
    # 4. If the field is diferent, update it in the json data list.
    # 5. Call the function to write the new data.

    # Give the updated data for write.
    def update_local_storage(self, new_data):
        try:
            with open(STORAGE_FILE, 'w') as file:
                json.dump(new_data, file, indent=4)
        except OSError as e:
            print(e)
        except FileExistsError as e:
            print(e)