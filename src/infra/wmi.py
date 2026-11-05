"""Captura de almacenamiento mediante WMI COM (sin PowerShell)."""

from __future__ import annotations

import os
import re
from typing import Any

from src.infra.units import bytes_to_gib
from src.models.storage import StorageDrive


def _extract_device_id(reference: Any) -> str | None:
    """Extrae ``DeviceID`` de una referencia WMI (string o objeto)."""
    text = str(reference)
    match = re.search(r'DeviceID="([^"]*)"', text)
    if match:
        value = match.group(1)
    else:
        text = text.strip().strip('"')
        value = text or None
    if value is None:
        return None
    # Las referencias WMI escapan las barras invertidas.
    return value.replace("\\\\", "\\").strip() or None


_BUS_TYPE_MAP = {
    1: "SCSI",
    2: "ATAPI",
    3: "ATA",
    4: "1394",
    5: "SSA",
    6: "Fibre",
    7: "USB",
    8: "RAID",
    9: "iSCSI",
    10: "SAS",
    11: "SATA",
    12: "SD",
    13: "MMC",
    14: "MAX",
    15: "Virtual",
    16: "Storage Spaces",
    17: "NVMe",
}


def _normalize_interface(raw: str | None, bus_type: int | None) -> str | None:
    if bus_type in _BUS_TYPE_MAP:
        return _BUS_TYPE_MAP[bus_type]
    text = (raw or "").strip().lower()
    if "usb" in text:
        return "USB"
    if "nvme" in text:
        return "NVMe"
    if "sata" in text or "serial ata" in text:
        return "SATA"
    if "scsi" in text:
        return "SCSI"
    if "raid" in text:
        return "RAID"
    return raw.strip() if raw else None


def _normalize_media(raw: str | None, media_type_code: int | None) -> str | None:
    if media_type_code == 3:
        return "HDD"
    if media_type_code == 4:
        return "SSD"
    if media_type_code == 5:
        return "SCM"
    text = (raw or "").strip().lower()
    if "ssd" in text or "solid state" in text:
        return "SSD"
    if "removable" in text:
        return "Removable"
    if "fixed" in text or "hard disk" in text:
        return "HDD"
    return raw.strip() if raw else None


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _msft_enrichment() -> dict[str, tuple[int | None, int | None]]:
    """Devuelve {serial/model key: (bus_type, media_type)} desde MSFT_PhysicalDisk."""
    result: dict[str, tuple[int | None, int | None]] = {}
    try:
        import win32com.client

        locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        svc = locator.ConnectServer(".", r"root\Microsoft\Windows\Storage")
        for disk in svc.ExecQuery("SELECT SerialNumber, BusType, MediaType FROM MSFT_PhysicalDisk"):
            serial = (getattr(disk, "SerialNumber", None) or "").strip()
            if not serial:
                continue
            result[serial] = (
                _to_int(getattr(disk, "BusType", None)),
                _to_int(getattr(disk, "MediaType", None)),
            )
    except Exception:  # noqa: BLE001 - opcional y puede requerir privilegios
        return result
    return result


def collect_memory_modules() -> list[dict]:
    """Devuelve los módulos RAM como lista de diccionarios (compatibles con DimmRam)."""
    result = []
    try:
        import win32com.client

        locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        svc = locator.ConnectServer(".", "root\\cimv2")
        for mem in svc.ExecQuery(
            "SELECT Caption, Manufacturer, PartNumber, Model, Tag, BankLabel, "
            "Capacity, Speed, ConfiguredClockSpeed, ConfiguredVoltage, DeviceLocator "
            "FROM Win32_PhysicalMemory"
        ):
            result.append(
                {
                    "Caption": getattr(mem, "Caption", None),
                    "Manufacturer": getattr(mem, "Manufacturer", None),
                    "PartNumber": getattr(mem, "PartNumber", None),
                    "Model": getattr(mem, "Model", None),
                    "Tag": getattr(mem, "Tag", None),
                    "BankLabel": getattr(mem, "BankLabel", None),
                    "Capacity": getattr(mem, "Capacity", None),
                    "Speed": getattr(mem, "Speed", None),
                    "ConfiguredClockSpeed": getattr(mem, "ConfiguredClockSpeed", None),
                    "ConfiguredVoltage": getattr(mem, "ConfiguredVoltage", None),
                    "DeviceLocator": getattr(mem, "DeviceLocator", None),
                }
            )
    except Exception:  # noqa: BLE001
        return result
    return result
    """Devuelve la lista de discos físicos con sus letras y rol de sistema."""
    try:
        import win32com.client
    except ImportError:
        return []

def collect_storage_drives(system_drive: str | None = None) -> list[StorageDrive]:
    """Devuelve la lista de discos físicos con sus letras y rol de sistema."""
    if system_drive is None:
        system_drive = os.getenv("SystemDrive", "C:")
    system_drive = system_drive.strip().rstrip("\\/").upper()
    if not system_drive.endswith(":"):
        system_drive += ":"

    drives: dict[str, StorageDrive] = {}

    try:
        import win32com.client

        locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        svc = locator.ConnectServer(".", "root\\cimv2")

        # 1. Discos físicos.
        for disk in svc.ExecQuery(
            "SELECT DeviceID, Model, SerialNumber, Size, InterfaceType, "
            "MediaType, Partitions FROM Win32_DiskDrive"
        ):
            device_id = getattr(disk, "DeviceID", None)
            if not device_id:
                continue
            device_id = str(device_id).strip()
            if device_id in drives:
                continue
            serial = (getattr(disk, "SerialNumber", None) or "").strip() or None
            drives[device_id] = StorageDrive(
                device_id=device_id,
                model=(getattr(disk, "Model", None) or "").strip() or None,
                serial_number=serial,
                size_bytes=_to_int(getattr(disk, "Size", None)),
                interface_type=(getattr(disk, "InterfaceType", None) or "").strip() or None,
                media_type=(getattr(disk, "MediaType", None) or "").strip() or None,
                partitions=_to_int(getattr(disk, "Partitions", None)),
            )

        # 2. Asociaciones disco -> partición (una consulta global).
        disk_to_partitions: dict[str, set[str]] = {key: set() for key in drives}
        for assoc in svc.ExecQuery(
            "SELECT Antecedent, Dependent FROM Win32_DiskDriveToDiskPartition"
        ):
            disk_id = _extract_device_id(getattr(assoc, "Antecedent", None))
            part_id = _extract_device_id(getattr(assoc, "Dependent", None))
            if disk_id in disk_to_partitions and part_id:
                disk_to_partitions[disk_id].add(part_id)

        # 3. Asociaciones partición -> disco lógico (una consulta global).
        partition_to_letters: dict[str, set[str]] = {}
        for assoc in svc.ExecQuery(
            "SELECT Antecedent, Dependent FROM Win32_LogicalDiskToPartition"
        ):
            part_id = _extract_device_id(getattr(assoc, "Antecedent", None))
            logical_id = _extract_device_id(getattr(assoc, "Dependent", None))
            if not part_id or not logical_id:
                continue
            letter = logical_id.strip().upper()
            if not letter.endswith(":"):
                letter = letter + ":"
            partition_to_letters.setdefault(part_id, set()).add(letter)

        # 4. Letras por disco.
        for device_id, drive in drives.items():
            letters: set[str] = set()
            for part_id in disk_to_partitions.get(device_id, ()):
                letters.update(partition_to_letters.get(part_id, ()))
            drive.drive_letters = sorted(letters)
            drive.is_system = system_drive in drive.drive_letters

        # 5. Enriquecimiento opcional con MSFT_PhysicalDisk.
        enrichment = _msft_enrichment()
        for drive in drives.values():
            if not drive.serial_number:
                continue
            bus_type, media_code = enrichment.get(drive.serial_number, (None, None))
            if bus_type is not None:
                drive.interface_type = _normalize_interface(
                    drive.interface_type, bus_type
                )
            if media_code is not None:
                drive.media_type = _normalize_media(drive.media_type, media_code)

        # 6. Normalizar interface/media para los discos sin enriquecimiento.
        for drive in drives.values():
            if drive.interface_type and drive.interface_type.lower() in {
                "ide", "scsi",
            }:
                drive.interface_type = _normalize_interface(drive.interface_type, None)
            if drive.media_type and drive.media_type.lower().startswith("fixed"):
                drive.media_type = "HDD"

    except Exception:  # noqa: BLE001 - WMI puede fallar; devolver lo que haya
        pass

    result = list(drives.values())
    # Sistema primero, luego por tamaño descendente.
    result.sort(key=lambda item: (not item.is_system, -(item.size_bytes or 0)))
    return result
