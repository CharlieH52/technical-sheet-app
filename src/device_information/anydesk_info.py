import os

from os import getlogin

ANYDESK_ERRORS = {
    'MAIN_PATH': "No se encuentra el directorio principal. Instala Anydesk.git",
    'READ_CONF_ERROR': "No se ha encontrado el archivo system.conf. Reinstala Anydesk.",
    'READ_ID_ERROR': "No se encuentra el ID dentro del archivo. Reinstala Anydesk"
}

class AnyDeskInfo:
    def __init__(self):
        self.user = getlogin()
        self.id_key = "ad.anynet.id"
        self.anydesk_path = f"C:/Users/{self.user}/AppData/Roaming/AnyDesk"
        self.config_file = f"C:/Users/{self.user}/AppData/Roaming/AnyDesk/system.conf"

    # Read .config file and return a dictionary.
    def read_config_file(self, file_path):
        config = {}
        with open(file_path, "r") as file:
            for line in file:
                key, value = line.strip().split('=', 1)
                config[key] = value
        return config

    # Verify the DEFAULT installation route.
    def verify_base_files(self):
        try:
            if os.path.exists(self.anydesk_path):
                try:
                    if os.path.exists(self.config_file):
                        ids = self.read_config_file(self.config_file)
                        if self.id_key in ids:
                            return True
                except OSError:
                    print(ANYDESK_ERRORS['READ_CONF_ERROR'])
            return False
        except OSError:
            print(ANYDESK_ERRORS['MAIN_PATH'])

    # Orchestrator
    def get_anydesk_desktop_id(self):
        verify = self.verify_base_files()
        if verify: 
            config_file = self.read_config_file(self.config_file)
            return config_file[self.id_key]