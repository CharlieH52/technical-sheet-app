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
                 storage_model: str,
                 storage_cap: int,
                 dimma_mark: str,
                 dimma_model: str,
                 dimma_cap: int,
                 dimmb_mark: str,
                 dimmb_model: str,
                 dimmb_cap: int,
                 anydesk_id: int
                ):
        
        self.device_name = device_name
        self.user_name = user_name
        self.machine_mac = machine_mac
        self.machine_ip = machine_ip
        self.mobo_mark = mobo_mark
        self.mobo_model = mobo_model
        self.cpu_info = cpu_info
        self.operative_system = operative_system
        self.storage_model = storage_model
        self.storage_cap = storage_cap
        self.dimm_1_mark = dimma_mark
        self.dimm_1_model = dimma_model
        self.dimm_1_cap = dimma_cap
        self.dimm_2_mark = dimmb_mark
        self.dimm_2_model = dimmb_model
        self.dimm_2_cap = dimmb_cap
        self.anydesk_id = anydesk_id

    def to_dictionary(self) -> dict[str, str | int]:
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
            'storage_model': self.storage_model,
            'storage_cap': self.storage_cap,
            'dimm_1_mark': self.dimm_1_mark,
            'dimm_1_model': self.dimm_1_model,
            'dimm_1_cap': self.dimm_1_cap,
            'dimm_2_mark': self.dimm_2_mark,
            'dimm_2_model': self.dimm_2_model,
            'dimm_2_cap': self.dimm_2_cap,
        }