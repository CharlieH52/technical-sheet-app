from app.command_processor import CommandProcessor
from app.models.ram import DimmRam

class HardwareInfo:
    def __init__(self):
        self.class_processor = ["powershell", "get-ciminstance", "-class Win32_Processor | Select-Object * | Format-List"]
        self.class_baseboard = ["powershell", "get-ciminstance", "-class Win32_BaseBoard | Select-Object * | Format-List"]
        self.class_diskdrive = ["powershell", "get-ciminstance", '-class Win32_DiskDrive | Where-Object { $_.DeviceID -like "*PHYSICALDRIVE0*" } | Format-List']
        self.class_physicalmemory = ["powershell", "get-ciminstance", '-class Win32_PhysicalMemory | Select-Object Caption, Manufacturer, PartNumber, Model, Tag, BankLabel, Capacity, Speed, ConfiguredClockSpeed, ConfiguredVoltage, DeviceLocator | ConvertTo-Json']
        self.cpu = CommandProcessor(self.class_processor).get_output_dictionary()
        self.baseboard = CommandProcessor(self.class_baseboard).get_output_dictionary()
        self.diskdrive = CommandProcessor(self.class_diskdrive).get_output_dictionary()
        self.physicalmemory = CommandProcessor(self.class_physicalmemory).get_from_json()

    # List dimm RAM
    def create_ram_objects(self) -> list[DimmRam]:
        dimm_list = []
        for dimm in self.physicalmemory:
            dimm_obj = DimmRam(
                caption=dimm.get("Caption"),
                manufacturer=dimm.get("Manufacturer"),
                part_number=dimm.get("PartNumber"),
                model=dimm.get("Model"),
                tag=dimm.get("Tag"),
                bank_label=dimm.get("BankLabel"),
                capacity=int(self._bytes_converter(dimm.get("Capacity"))),
                speed=int(dimm.get("Speed")),
                configured_clock_speed=dimm.get("ConfiguredClockSpeed"),
                configured_voltage=dimm.get("ConfiguredVoltage"),
                device_locator=dimm.get("DeviceLocator")
            )
            dimm_list.append(dimm_obj)
        return dimm_list

    # bits to bytes converter.
    def _bytes_converter(self, total_Bytes: int) -> int:
        calc = total_Bytes / (1024 ** 3)
        return int(calc)
    
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

    # MEMORY RAM
    # def get_memory_dimms(self):
    #     for dimm in self.physicalmemory:

    # def get_memory_dimm_a_manufacturer(self):
    #     return self.dimm_a.get("Manufacturer")

    # def get_memory_dimm_a_model(self):
    #     return self.dimm_a.get("PartNumber")
    
    # def get_memory_dimm_a_channel(self):
    #     return self.dimm_a.get("DeviceLocator")

    # def get_memory_dimm_a_cap(self) -> int:
    #     memory = self._bytes_converter(int(self.dimm_a.get("Capacity")))
    #     return memory
    
    # MAIN STORAGE
    # Obtain the model name of the main storage device.
    def get_disk_model(self):
        return self.diskdrive.get("Model")

    # Obtain the memory cap of the main storage device.
    def get_disk_cap(self) -> int:
        memory = self._bytes_converter(int(self.diskdrive.get("Size")))
        return memory
    
    # Get the full data about the main storage device.
    def get_main_storage(self):
        return f"{self.get_disk_cap()} {self.get_disk_model()}"
    