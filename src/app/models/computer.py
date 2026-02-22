from dataclasses import dataclass
from app.models.ram import DimmRam

@dataclass
class Computer:
    device_name: str
    user_name: str
    machine_mac: str
    machine_ip: str
    mobo_mark: str
    mobo_model: str
    cpu_info: str
    operative_system: str
    storage_model: str
    storage_cap: int
    anydesk_id: int
    dimm_list: list[DimmRam]

    def to_dictionary(self) -> dict[str, str | int | list]:
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
            'dimm_list': [dimm_obj.to_dictionary() for dimm_obj in self.dimm_list]
        }