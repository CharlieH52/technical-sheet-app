import socket
from app.device_information.device_information import DeviceInformation
from app.shared.directory_paths import *

dev = DeviceInformation()

class WriteFile:
    def __init__(self):
        self.file_path = socket.gethostname()
    def write(self):
        try:
            new_file = f'{self.file_path}.txt'
            with open(new_file, '+w') as file:
                for name, key in dev.device_info.items():
                    file.write(f'{name}: {key}\n')
            file.close()
        except OSError as e:
            print(e)
        except FileExistsError as e:
            print(e)