from dataclasses import dataclass, field
from src.models.ram import DimmRam
from src.models.storage import StorageDrive

@dataclass
class Computer:
    device_name: str
    user_name: str
    machine_mac: str
    machine_ip: str
    mobo_mark: str | None
    mobo_model: str | None
    cpu_info: str | None
    operative_system: str | None
    storage_model: str | None
    storage_cap: int | None
    anydesk_id: int | None
    dimm_list: list[DimmRam]
    storage_list: list[StorageDrive] = field(default_factory=list)
    device_uuid: str | None = None
    identity_source: str | None = None
    hardware_ids: dict | None = None
    captured_at: str | None = None
    remote_id: int | None = None

    @property
    def storage_count(self) -> int:
        return len(self.storage_list)

    def to_dictionary(self) -> dict[str, str | int | list | None | dict]:
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
            'dimm_list': [dimm_obj.to_dictionary() for dimm_obj in self.dimm_list],
            'storage_list': [drive.to_dictionary() for drive in self.storage_list],
            'storage_count': self.storage_count,
            'device_uuid': self.device_uuid,
            'identity_source': self.identity_source,
            'hardware_ids': self.hardware_ids,
            'captured_at': self.captured_at,
        }