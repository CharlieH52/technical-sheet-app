from src.command_processor import CommandProcessor
from psutil import disk_usage, virtual_memory

class HardwareInfo:
    GET_CPU_DATA = "wmic cpu get name /format:list"
    GET_MOBO_DATA = "wmic baseboard get product, manufacturer /format:list"
    GET_MAIN_STORAGE_DEVICE = "wmic diskdrive where index=0 get model /format:list"

    def __init__(self):
        self.cpu_data = CommandProcessor(self.GET_CPU_DATA).get_parsed_output()
        self.mobo_data = CommandProcessor(self.GET_MOBO_DATA).get_parsed_output()
        self.storage_data = CommandProcessor(self.GET_MAIN_STORAGE_DEVICE).get_parsed_output()

    # bits to bytes converter.
    def _bytes_converter(self, total_Bytes):
        return total_Bytes / (1024 ** 3)
    
    # CPU
    # Obtain the full name and the main specs about the processor.
    def get_cpu_model(self):
        return self.cpu_data['Name']
    
    # MOTHERBOARD
    # Obtain the model name. 
    def get_motherboard_model(self):
        return self.mobo_data['Product']

    # Obtain the name of the manufacturer.
    def get_motherboard_manufacturer(self):
        return self.mobo_data['Manufacturer']

    # MEMORY RAM
    # Obtain the memory cap of the installed memory.
    def get_total_memory_ram(self):
        totalMemory = virtual_memory().total
        systemMemory = f"{round(self._bytes_converter(totalMemory), 0)} GB"
        return systemMemory
    
    # MAIN STORAGE
    # Obtain the model name of the main storage device.
    def _get_disk_model(self):
        return self.storage_data['Model']

    # Obtain the memory cap of the main storage device.
    def _get_storage_cap(self):
        totalStorage = disk_usage("C:\\").total
        systemStorage = f"{round(self._bytes_converter(totalStorage), 0)} GB"
        return systemStorage
    
    # Get the full data about the main storage device.
    def get_main_storage(self):
        return f"{self._get_storage_cap()} {self._get_disk_model()}"
    