"""Información de hardware.

En esta etapa CPU y placa base se leen del registro (sin PowerShell). El
almacenamiento y la RAM siguen usando WMI vía PowerShell hasta las etapas de
``psutil``/``pywin32``; por eso aquí solo se eliminaron las dos consultas que ya
tenían reemplazo nativo.
"""

from src.command_processor import CommandProcessor
from src.infra.diagnostics import diagnostics
from src.infra.hardware_registry import read_cpu_name, read_motherboard
from src.models.ram import DimmRam


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

        # Pendiente de migrar a WMI COM / psutil en las siguientes etapas.
        self.class_diskdrive = [
            "powershell",
            "get-ciminstance",
            '-class Win32_DiskDrive | Where-Object { $_.DeviceID -like "*PHYSICALDRIVE0*" } | Format-List',
        ]
        self.class_physicalmemory = [
            "powershell",
            "get-ciminstance",
            '-class Win32_PhysicalMemory | Select-Object Caption, Manufacturer, PartNumber, Model, Tag, BankLabel, Capacity, Speed, ConfiguredClockSpeed, ConfiguredVoltage, DeviceLocator | ConvertTo-Json',
        ]
        self.diskdrive = {}
        try:
            self.diskdrive = CommandProcessor(self.class_diskdrive).get_output_dictionary()
        except Exception as exc:  # noqa: BLE001 - WMI/PowerShell puede fallar
            diagnostics.warn(f"Win32_DiskDrive no disponible: {exc}")

        self.physicalmemory = []
        try:
            self.physicalmemory = CommandProcessor(self.class_physicalmemory).get_from_json()
        except Exception as exc:  # noqa: BLE001 - WMI/PowerShell puede fallar
            diagnostics.warn(f"Win32_PhysicalMemory no disponible: {exc}")

        diagnostics.record("storage_model", self.get_disk_model(), "powershell")
        diagnostics.record(
            "storage_cap",
            self.get_disk_cap(),
            "powershell",
            note="valor en GiB; pendiente migrar a bytes (etapa de almacenamiento)",
        )

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

    # bytes to GiB converter (compatibilidad con la BD/API actual de DIMM).
    def _bytes_converter(self, total_bytes: int | None) -> int | None:
        if total_bytes is None:
            return None
        return int(total_bytes / (1024 ** 3))

    # CPU
    # Obtain the full name and the main specs about the processor.
    def get_cpu_model(self):
        return self.cpu.get("Name")

    # MOTHERBOARD
    # Obtain the model name.
    def get_motherboard_model(self):
        return self.baseboard.get("Product")

    # Obtain the name of the manufacturer.
    def get_motherboard_manufacturer(self):
        return self.baseboard.get("Manufacturer")

    # MAIN STORAGE
    # Obtain the model name of the main storage device.
    def get_disk_model(self):
        return self.diskdrive.get("Model")

    # Obtain the memory cap of the main storage device.
    def get_disk_cap(self) -> int | None:
        size = self._as_int(self.diskdrive.get("Size"))
        return self._bytes_converter(size)

    # Get the full data about the main storage device.
    def get_main_storage(self):
        return f"{self.get_disk_cap()} {self.get_disk_model()}"
