from platform import node

from src.object.computer_object import Computer

class ComputerBuilder:
    def __init__(self, network_provider, user_provider, hardware_provider, system_provider, anydesk_provider):
        self.network = network_provider
        self.hardware = hardware_provider
        self.system = system_provider
        self.anydesk = anydesk_provider
        self.user = user_provider

    def get_all_data(self) -> Computer:
        self.network.get_info()
        return Computer(device_name = node(),
                       user_name = self.user.get_full_name(),
                       machine_mac = self.network.network_info['MAC'],
                       machine_ip = self.network.network_info['IP4'],
                       mobo_mark = self.hardware.get_motherboard_manufacturer(),
                       mobo_model = self.hardware.get_motherboard_model(),
                       cpu_info = self.hardware.get_cpu_model(),
                       operative_system = self.system.get_windows_version(),
                       storage = self.hardware.get_main_storage(),
                       memory_cap = self.hardware.get_total_memory_ram(),
                       anydesk_id = self.anydesk.get_anydesk_desktop_id()
                        )