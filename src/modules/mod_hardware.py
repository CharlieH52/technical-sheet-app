from src.command_processor import CommandProcessor
from psutil import disk_usage, virtual_memory

class HardwareInfo:
    def __init__(self):
        self.class_processor = "Win32_Processor"
        self.class_baseboard = "Win32_BaseBoard"
        self.class_diskdrive = "Win32_DiskDrive"
        self.cpu = CommandProcessor(self.class_processor).get_parsed_output()
        self.baseboard = CommandProcessor(self.class_baseboard).get_parsed_output()
        self.diskdrive = CommandProcessor(self.class_diskdrive).get_parsed_output()

    # bits to bytes converter.
    def _bytes_converter(self, total_Bytes):
        return total_Bytes / (1024 ** 3)
    
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
    # Obtain the memory cap of the installed memory.
    def get_total_memory_ram(self):
        totalMemory = virtual_memory().total
        systemMemory = f"{round(self._bytes_converter(totalMemory), 0)}"
        return systemMemory
    
    # MAIN STORAGE
    # Obtain the model name of the main storage device.
    def get_disk_model(self):
        return self.diskdrive.get("Model")

    # Obtain the memory cap of the main storage device.
    def get_storage_cap(self):
        totalStorage = disk_usage("C:\\").total
        systemStorage = f"{round(self._bytes_converter(totalStorage), 0)}"
        return systemStorage
    
    # Get the full data about the main storage device.
    def get_main_storage(self):
        return f"{self.get_storage_cap()} {self.get_disk_model()}"
    