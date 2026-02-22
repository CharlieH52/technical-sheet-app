from dataclasses import dataclass

@dataclass
class DimmRam:
    caption: str
    manufacturer: str
    part_number: str
    model: str
    tag: str
    bank_label: str
    device_locator: str
    capacity: int = 0
    speed: int = 0
    configured_clock_speed: int = 0
    configured_voltage: int = 0
    
    def to_dictionary(self) -> dict[str, str | int]:
        return {
            'Caption': self.caption,
            'Manufacturer': self.manufacturer,
            'PartNumber': self.part_number,
            'Model': self.model,
            'Tag': self.tag,
            'BankLabel': self.bank_label,
            'Capacity': self.capacity,
            'Speed': self.speed,
            'ConfiguredClockSpeed': self.configured_clock_speed,
            'ConfiguredVoltage': self.configured_voltage,
            'DeviceLocator': self.device_locator
        }