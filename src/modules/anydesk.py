import os
from os import getlogin

class AnyDeskInfo:
    MAIN_PATH_ERROR = "Default path: C:/Users/current_user/AppData/Roaming/AnyDesk\nERROR: Not found.\nPlease, verify the route manually."
    FILE_PATH_ERROR = "Default file path: C:/Users/current_user/AppData/Roaming/AnyDesk/system.conf\nERROR: Not found.\nTry reinstall Anydesk."
    # READ_ID_ERROR = "ID key: ad.anynet.id\nERROR: The key is not in system.conf.\nTry to connect with a remote desktop to generate it or reinstall Anydesk."

    def __init__(self):
        self.user = getlogin()
        self.id_key = "ad.anynet.id"
        self.anydesk_path = f"C:/Users/{self.user}/AppData/Roaming/AnyDesk"
        self.config_file = f"C:/Users/{self.user}/AppData/Roaming/AnyDesk/system.conf"
        self.none_id = "0000000000"

    # Read .config file and return a dictionary.
    # For Python older version than 3.10 change None for Optional from typing...
    def __read_config_file(self, file_path: str) -> dict[str, str] | None:
        config = {}
        try:
            with open(file_path, "r") as file:
                for line in file:
                    key, value = line.strip().split('=', 1)
                    config[key] = value
            return config
        except (FileNotFoundError, OSError):
            print(self.FILE_PATH_ERROR)
            return None

    # Check the DEFAULT installation route.
    def __check_installation_path(self) -> bool:
        try:
            return os.path.exists(self.anydesk_path)
        except OSError:
            print(self.MAIN_PATH_ERROR)
            return False
        
    def __check_conf_file(self) -> bool:
        try:
            return os.path.exists(self.config_file)
        except OSError:
            print(self.FILE_PATH_ERROR)
            return False
        
    def __check_desktop_id(self) -> bool:
        keys = self.__read_config_file(self.config_file)
        if keys is None:
            return False 
        return any(self.id_key in key for key, _ in keys)
                
    def __check_integrity(self) -> bool:
        if not self.__check_installation_path():
            return False

        if not self.__check_conf_file():
            return False
        
        if not self.__check_desktop_id():
            return False
        
        return True

    # Orchestrator
    def get_anydesk_desktop_id(self) -> str:
        verify = self.__check_integrity()
        if verify: 
            config_keys = self.__read_config_file(self.config_file)
            if config_keys is None:
                return self.none_id
            return config_keys.get(config_keys[self.id_key], self.none_id)
        return self.none_id