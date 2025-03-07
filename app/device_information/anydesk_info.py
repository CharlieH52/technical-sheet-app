import os
import re

from app.shared.directory_paths import *
from app.shared.error_messages import ERROR_PRINTS

class AnyDeskInfo:
    def __init__(self):
        self.anyid = self.get_anydesk_desktop_id()

    # Obtiene el ID de escritorio de AnyDesk.
    def get_anydesk_desktop_id(self):
        def _files_checker():
            try:
                if not os.path.isdir(folderAnyDesk):
                    return "Instalacion defectuosa o inexistente."
            except OSError:
                print(ERROR_PRINTS['MAIN_PATH'])

            try:
                if not os.path.isfile(configFile):
                    return "Capturar manualmente."
            except OSError:
                print(ERROR_PRINTS['READ_CONF_ERROR'])
            
            return None
                    
        def _read_id():
            regEx = r".id=([0-9]*)"
            with open(configFile, 'r') as file:
                for line in file:
                    anyID = re.search(regEx, line)
                    if anyID:
                        return anyID.group(1)
        
        if _files_checker() == None:
            return _read_id()