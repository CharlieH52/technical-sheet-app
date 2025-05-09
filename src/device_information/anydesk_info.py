import os
import re

from os import getlogin

ANYDESK_ERRORS = {
    'MAIN_PATH': "No se encuentra el directorio principal. Instala Anydesk.git",
    'READ_CONF_ERROR': "No se ha encontrado el archivo system.conf. Reinstala Anydesk.",
    'READ_ID_ERROR': "No se encuentra el ID dentro del archivo. Reinstala Anydesk"
}

user = getlogin()

class AnyDeskInfo:
    def __init__(self):
        self.anydesk_path = f'C:/Users/{user}/AppData/Roaming/AnyDesk'
        self.config_file = f'C:/Users/{user}/AppData/Roaming/AnyDesk/system.conf'

    # Get the desktop ID of AnyDesk.
    def get_anydesk_desktop_id(self):
        # Verify the NORMAL installation route and the .conf file with the ID.
        def _files_checker():
            try:
                if not os.path.exists(self.anydesk_path):
                    return "AnyDesk is not installed or the installation directory is different."
            except OSError:
                print(ANYDESK_ERRORS['MAIN_PATH'])

            try:
                if not os.path.exists(self.config_file):
                    return "Type the ID manually."
            except OSError:
                print(ANYDESK_ERRORS['READ_CONF_ERROR'])
            
            return None
                    
        def _read_id():
            regEx = r".id=([0-9]*)"
            with open(self.config_file, 'r') as file:
                for line in file:
                    anyID = re.search(regEx, line)
                    if anyID:
                        return anyID.group(1)
        
        if _files_checker() == None:
            return _read_id()