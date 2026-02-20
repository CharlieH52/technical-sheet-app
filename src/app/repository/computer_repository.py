import os
import json
from app.notifications.popup import PopUp
from socket import gethostname

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
    def load_local_storage(self) -> list[dict[str,str | int | dict[str,str]]]:
        current_data = []
        try:
            with open(self.STORAGE_FILE, "r") as file:
                current_data = json.load(file)
        except OSError as e:
            print(f"Error alcanzado. {e}")
        except json.JSONDecodeError as e:
            current_data = []
        return current_data
    # Give the updated data for write.
    def save_data_in_file(self, new_data):
        try:
            with open(self.STORAGE_FILE, "w") as file:
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
                    PopUp("Estado", "Registro actualizado correctamente.")
                return
        current_data.append(new_registry)
        self.save_data_in_file(current_data)
        PopUp("Estado", "Ficha guardada correctamente.")

# class ComputerRepositoryPostgres:
    
#     load_dotenv()

#     def __init__(self) -> None:
#         self.USER = os.getenv("user")
#         self.PASSWORD = os.getenv("password")
#         self.HOST = os.getenv("host")
#         self.PORT = os.getenv("port")
#         self.DBNAME = os.getenv("dbname")

#     def post_computer_on_database(self):
#         try:
#             connection = psycopg2.connect(
#                 user=self.USER,
#                 password=self.PASSWORD,
#                 host=self.HOST,
#                 port=self.PORT,
#                 dbname=self.DBNAME
#             )
#             cursor = connection.cursor()
            
#             cursor.execute("SELECT NOW();")
#             result = cursor.fetchone()
#             print("Current Time:", result)

#             # Close the cursor and connection
#             cursor.close()
#             connection.close()
#             print("Connection closed.")

#         except Exception as e:
#             print(f"Failed to connect: {e}")
