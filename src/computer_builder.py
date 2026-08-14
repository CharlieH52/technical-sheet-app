from src.models.computer import Computer
from platform import node


class ComputerBuilder:
    def __init__(self, network_provider, user_provider, hardware_provider, system_provider, anydesk_provider):
        self.network = network_provider
        self.hardware = hardware_provider
        self.system = system_provider
        self.anydesk = anydesk_provider
        self.user = user_provider
    
    def create_computer(self) -> Computer:
        return Computer(
            device_name = node(),
            user_name = self.user.get_domain_name(),
            machine_mac = self.network.get_mac_address(),
            machine_ip = self.network.get_ip_address(),
            mobo_mark = self.hardware.get_motherboard_manufacturer(),
            mobo_model = self.hardware.get_motherboard_model(),
            cpu_info = self.hardware.get_cpu_model(),
            operative_system = self.system.get_windows_version(),
            storage_model = self.hardware.get_disk_model(),
            storage_cap= self.hardware.get_disk_cap(),
            anydesk_id = self.anydesk.get_anydesk_desktop_id(),
            dimm_list = self.hardware.create_ram_objects()
            )