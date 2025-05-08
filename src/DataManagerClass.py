import os
import json

from platform import node
from socket import gethostname

from src.device_information.anydesk_info import AnyDeskInfo
from src.device_information.hardware_info import HardwareInfo
from src.device_information.network_info import NetworkInfo
from src.device_information.system_info import SystemInfo

from src.classes.ComputerClass import Computer

computer_name = gethostname()
working_path = os.getcwd()
file_name = f'{computer_name}.json'
new_file_path = os.path.join(working_path, file_name)

net = NetworkInfo()

class DataManager:
    def __init__(self):
        self.machine_name = node()
        # self.computer = Computer(device_name=self.machine_name,
        #                          user_domain_name=None,
        #                          machine_mac=net.network_info['MAC'],
        #                          machine_ip=net.network_info['IP4'],
        #                          mobo_mark=HardwareInfo.get_motherboard_manufacturer(),
        #                          mobo_model=HardwareInfo.get_motherboard_model(),
        #                          cpu_info=HardwareInfo.get_cpu_model,
        #                          operative_system=SystemInfo.get_windows_version(),
        #                          storage=HardwareInfo.get_main_storage(),
        #                          memory_cap=HardwareInfo.get_total_memory_ram(),
        #                          anydesk_id=AnyDeskInfo.get_anydesk_desktop_id()
        #                         )
    

    def write_json_storage(self):
        try:
            pass
            # with open(new_file, '+w') as file:
            #     for name, key in dev.device_info.items():
            #         file.write(f'{name}: {key}\n')
        except OSError as e:
            print(e)
        except FileExistsError as e:
            print(e)