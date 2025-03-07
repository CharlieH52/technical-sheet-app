from os import getlogin
from platform import node

# MAIN_DATA
machine_name = node()

# AnyDesk
folderAnyDesk = f'C:/Users/{getlogin()}/AppData/Roaming/AnyDesk'
configFile = f'C:/Users/{getlogin()}/AppData/Roaming/AnyDesk/system.conf'