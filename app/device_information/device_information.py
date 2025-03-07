from app.device_information.anydesk_info import AnyDeskInfo
from app.device_information.hardware_info import HardwareInfo
from app.device_information.network_info import NetworkInfo
from app.device_information.system_info import SystemInfo

from app.shared.directory_paths import *

class DeviceInformation:
    def __init__(self):
        # Catcher modules
        self.adi = AnyDeskInfo()
        self.had = HardwareInfo()
        self.net = NetworkInfo()
        self.sys = SystemInfo()

        # Catch the device info when the program starts
        self.device_info = self._get_internal_info()

    def _get_internal_info(self):
        machine_information = {
            'DeviceName': machine_name,
            'UserDomainName': self.sys.get_system_user_name(),
            'MachineMAC': self.net.network_info['MAC'],
            'MachineIP': self.net.network_info['IP4'],
            'AnyDeskID': self.adi.get_anydesk_desktop_id(),
            'MoboMark':  self.had.get_motherboard_manufacturer(),
            'MoboModel': self.had.get_motherboard_model(),
            'CPUInformation': self.had.get_cpu_model(),
            'OperativeSystem': self.sys.get_windows_version(),
            'Storage': self.had.get_main_storage(),
            'MemoryCap': self.had.get_total_memory_ram()

        }
        return machine_information