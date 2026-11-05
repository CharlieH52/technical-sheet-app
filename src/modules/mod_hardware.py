"""Información de hardware.

CPU y placa base se leen del registro. La RAM sigue vía PowerShell (WMI COM
pendiente) pero con valores nulos tolerados. El almacenamiento se captura con
WMI COM (N unidades) y el disco del sistema se detecta por ``%SystemDrive%``.
"""

from __future__ import annotations

from src.command_processor import CommandProcessor
from src.infra.diagnostics import diagnostics
from src.infra.diskinfo import read_system_disk, system_drive
from src.infra.hardware_registry import read_cpu_name, read_motherboard
from src.infra.units import bytes_to_gib
from src.infra.wmi import collect_memory_modules, collect_storage_drives
from src.models.ram import DimmRam
from src.models.storage import StorageDrive

try:  # pragma: no cover - psutil es dependencia obligatoria
    import psutil
except ImportError:  # pragma: no cover
    psutil = None


class HardwareInfo:
    def __init__(self):
        cpu_name, cpu_source = read_cpu_name()
        board = read_motherboard()

        self.cpu = {"Name": cpu_name}
        self.baseboard = {
            "Manufacturer": board.manufacturer,
            "Product": board.product,
            "Version": board.version,
        }

        diagnostics.record("cpu_info", cpu_name, cpu_source)
        diagnostics.record("mobo_mark", board.manufacturer, board.source)
        diagnostics.record("mobo_model", board.product, board.source)

        # RAM total y disco del sistema con psutil.
        self.ram_total_bytes = None
        self.ram_total_gib = None
        if psutil is not None:
            try:
                self.ram_total_bytes = int(psutil.virtual_memory().total)
                self.ram_total_gib = bytes_to_gib(self.ram_total_bytes)
            except Exception as exc:  # noqa: BLE001
                diagnostics.warn(f"psutil.virtual_memory no disponible: {exc}")
        diagnostics.record("ram_total_gib", self.ram_total_gib, "psutil")

        self.system_disk = read_system_disk()
        diagnostics.record("system_drive", self.system_disk.drive, self.system_disk.source)
        diagnostics.record(
            "system_disk_total_gib",
            bytes_to_gib(self.system_disk.total_bytes),
            "psutil",
        )
        diagnostics.record(
            "system_disk_free_gib",
            bytes_to_gib(self.system_disk.free_bytes),
            "psutil",
        )

        # Almacenamiento: N unidades vía WMI COM.
        self.storage_list: list[StorageDrive] = collect_storage_drives(system_drive())
        diagnostics.record("storage_count", len(self.storage_list), "wmi")
        if self.storage_list:
            diagnostics.record(
                "storage_model",
                self.storage_list[0].model,
                "wmi",
                note="disco de sistema (primer elemento tras ordenar)",
            )
        else:
            diagnostics.warn("No se detectaron unidades de almacenamiento.")

        # Compatibilidad con la API anterior: resumen del disco de sistema.
        system_drive_obj = next(
            (drive for drive in self.storage_list if drive.is_system),
            self.storage_list[0] if self.storage_list else None,
        )
        self.diskdrive = {
            "Model": system_drive_obj.model if system_drive_obj else None,
            "Size": system_drive_obj.size_bytes if system_drive_obj else None,
        }

        # RAM vía WMI COM.
        self.physicalmemory = collect_memory_modules()
        diagnostics.record("ram_modules", len(self.physicalmemory), "wmi")

    # List dimm RAM
    def create_ram_objects(self) -> list[DimmRam]:
        raw = self.physicalmemory
        if isinstance(raw, dict):
            raw = [raw]
        elif not isinstance(raw, list):
            raw = []

        dimm_list = []
        for dimm in raw:
            if not isinstance(dimm, dict):
                continue
            dimm_obj = DimmRam(
                caption=dimm.get("Caption"),
                manufacturer=dimm.get("Manufacturer"),
                part_number=dimm.get("PartNumber"),
                model=dimm.get("Model"),
                tag=dimm.get("Tag"),
                bank_label=dimm.get("BankLabel"),
                capacity=self._bytes_converter(self._as_int(dimm.get("Capacity"))),
                speed=self._as_int(dimm.get("Speed")),
                configured_clock_speed=self._as_int(dimm.get("ConfiguredClockSpeed")),
                configured_voltage=self._as_int(dimm.get("ConfiguredVoltage")),
                device_locator=dimm.get("DeviceLocator"),
            )
            dimm_list.append(dimm_obj)
        return dimm_list

    @staticmethod
    def _as_int(value: object) -> int | None:
        try:
            return int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return None

    def _bytes_converter(self, total_bytes: int | None) -> int | None:
        if total_bytes is None:
            return None
        return int(total_bytes / (1024 ** 3))

    def get_cpu_model(self):
        return self.cpu.get("Name")

    def get_motherboard_model(self):
        return self.baseboard.get("Product")

    def get_motherboard_manufacturer(self):
        return self.baseboard.get("Manufacturer")

    # Almacenamiento (bytes, no GiB).
    def get_disk_model(self):
        return self.diskdrive.get("Model")

    def get_disk_cap(self) -> int | None:
        return self._as_int(self.diskdrive.get("Size"))

    def get_main_storage(self):
        return f"{self.get_disk_cap()} {self.get_disk_model()}"

    def get_storage_list(self) -> list[StorageDrive]:
        return list(self.storage_list)
