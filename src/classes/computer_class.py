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
            'device_name': self.device_name,
            'user_domain_name': self.user_domain_name,
            'machine_mac': self.machine_mac,
            'machine_ip': self.machine_ip,
            'mobo_mark':  self.mobo_mark,
            'mobo_model': self.mobo_model,
            'cpu_info': self.cpu_info,
            'operative_system': self.operative_system,
            'storage': self.storage,
            'memory_cap': self.memory_cap,
            'anydesk_id': self.anydesk_id
        }