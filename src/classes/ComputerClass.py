class Computer:
    def __init__(self, device_name, user_domain_name, machine_mac, machine_ip, mobo_mark, mobo_model, cpu_info, operative_system, storage, memory_cap, anydesk_id):
        self.device_name = device_name
        self.user_domain_name = user_domain_name
        self.machine_mac = machine_mac
        self.machine_ip = machine_ip
        self.mobo_mark = mobo_mark
        self.mobo_model = mobo_model
        self.cpu_info = cpu_info
        self.operative_system = operative_system
        self.storage = storage
        self.memory_cap = memory_cap
        self.anydesk_id = anydesk_id

    def to_dictionary(self):
        return {
            'DeviceName': self.device_name,
            'UserDomainName': self.user_domain_name,
            'MachineMAC': self.machine_mac,
            'MachineIP': self.machine_ip,
            'MoboMark':  self.mobo_mark,
            'MoboModel': self.mobo_model,
            'CPUInformation': self.cpu_info,
            'OperativeSystem': self.operative_system,
            'Storage': self.storage,
            'MemoryCap': self.memory_cap,
            'AnyDeskID': self.anydesk_id
        }