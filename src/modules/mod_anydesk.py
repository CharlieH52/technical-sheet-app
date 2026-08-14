import os
from src.notifications.popup import PopUp

class AnyDeskInfo:
    def __init__(self):
        self.user = os.getlogin()
        self.id_key = "ad.anynet.id"
        self.anydesk_path = f"C:/Users/{self.user}/AppData/Roaming/AnyDesk"
        self.config_file = f"C:/Users/{self.user}/AppData/Roaming/AnyDesk/system.conf"
        self.none_id = 0

    # Read .config file and return a dictionary.
    # For Python older version than 3.10 change None for Optional from typing...
    def __read_config_file(self, file_path: str) -> dict[str, str] | None:
        config = {}
        try:
            with open(file_path, "r") as file:
                for line in file:
                    key, space, value = line.partition('=')
                    if not space:
                        continue
                    config[key.strip()] = value.strip()
            return config
        except (FileNotFoundError, OSError):
            PopUp('Error', f'Config file not found. Check the default path: {self.config_file}.')
            return None

    # Check the DEFAULT installation route.
    def __check_installation_path(self) -> bool:
        try:
            return os.path.exists(self.anydesk_path)
        except OSError:
            PopUp('Error', f'Is Anydesk installed?, please verify the installation default path: {self.anydesk_path}.')
            return False
        
    def __check_conf_file(self) -> bool:
        try:
            return os.path.exists(self.config_file)
        except OSError:
            PopUp('Error', f'Config file not found, please verify system.conf file path: {self.config_file}.')
            return False
        
    def __check_desktop_id(self) -> bool:
        keys = self.__read_config_file(self.config_file)
        if keys is None:
            return False 
        return any(self.id_key in key for key, value in keys.items())
                
    def __check_integrity(self) -> bool:
        if not self.__check_installation_path():
            return False

        if not self.__check_conf_file():
            return False
        
        if not self.__check_desktop_id():
            return False
        
        return True

    # Orchestrator
    def get_anydesk_desktop_id(self) -> int:
        verify = self.__check_integrity()
        if verify: 
            config_keys = self.__read_config_file(self.config_file)
            if config_keys is None:
                PopUp('Desktop ID missed', 'Please, verify your Anydesk installation.')
                return self.none_id
            return int(config_keys.get(self.id_key, self.none_id))
        return self.none_id