class Computer:
    def __init__(self,
                 device_name: str, 
                 user_name: str,
                 machine_mac: str,
                 machine_ip: str,
                 mobo_mark: str,
                 mobo_model: str,
                 cpu_info: str,
                 operative_system: str,
                 storage: str,
                 memory_cap: str,
                 anydesk_id: str
                ):
        
        self.device_name = device_name
        self.user_name = user_name
        self.machine_mac = machine_mac
        self.machine_ip = machine_ip
        self.mobo_mark = mobo_mark
        self.mobo_model = mobo_model
        self.cpu_info = cpu_info
        self.operative_system = operative_system
        self.storage = storage
        self.memory_cap = memory_cap
        self.anydesk_id = anydesk_id

    def to_dictionary(self) -> dict[str, str]:
        return {
            'anydesk_id': self.anydesk_id,
            'device_name': self.device_name,
            'user_name': self.user_name,
            'machine_mac': self.machine_mac,
            'machine_ip': self.machine_ip,
            'mobo_mark':  self.mobo_mark,
            'mobo_model': self.mobo_model,
            'cpu_info': self.cpu_info,
            'operative_system': self.operative_system,
            'storage': self.storage,
            'memory_cap': self.memory_cap
        }