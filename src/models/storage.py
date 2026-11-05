"""Modelo de una unidad de almacenamiento física."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StorageDrive:
    device_id: str
    model: str | None = None
    serial_number: str | None = None
    size_bytes: int | None = None
    interface_type: str | None = None
    media_type: str | None = None
    partitions: int | None = None
    drive_letters: list[str] = field(default_factory=list)
    is_system: bool = False

    def to_dictionary(self) -> dict:
        return {
            "device_id": self.device_id,
            "model": self.model,
            "serial_number": self.serial_number,
            "size_bytes": self.size_bytes,
            "interface_type": self.interface_type,
            "media_type": self.media_type,
            "partitions": self.partitions,
            "drive_letters": list(self.drive_letters),
            "is_system": self.is_system,
        }

    def describe(self) -> str:
        size = ""
        if self.size_bytes:
            size = f" {self.size_bytes / (1024 ** 3):.0f} GB"
        suffix = " (sistema)" if self.is_system else ""
        return f"{self.model or self.device_id}{size}{suffix}".strip()
