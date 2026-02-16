from app.command_processor import CommandProcessor

class HardwareInfo:
    def __init__(self):
        self.class_processor = ["powershell", "get-ciminstance", "-class Win32_Processor | Select-Object * | Format-List"]
        self.class_baseboard = ["powershell", "get-ciminstance", "-class Win32_BaseBoard | Select-Object * | Format-List"]
        self.class_diskdrive = ["powershell", "get-ciminstance", '-class Win32_DiskDrive | Where-Object { $_.DeviceID -like "*PHYSICALDRIVE0*" } | Format-List']
        self.class_dimm_1 = ["powershell", "get-ciminstance", '-class Win32_PhysicalMemory | Where-Object { $_.DeviceLocator -like "*ChannelA*" } | Format-List']
        self.class_dimm_2 = ["powershell", "get-ciminstance", '-class Win32_PhysicalMemory | Where-Object { $_.DeviceLocator -like "*ChannelB*" } | Format-List']
        self.cpu = CommandProcessor(self.class_processor).get_output_dictionary()
        self.baseboard = CommandProcessor(self.class_baseboard).get_output_dictionary()
        self.diskdrive = CommandProcessor(self.class_diskdrive).get_output_dictionary()
        self.dimm_a = CommandProcessor(self.class_dimm_1).get_output_dictionary()
        self.dimm_b = CommandProcessor(self.class_dimm_2).get_output_dictionary()

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
    # DIMM A
    def get_memory_dimm_a_manufacturer(self):
        return self.dimm_a.get("Manufacturer")

    def get_memory_dimm_a_model(self):
        return self.dimm_a.get("PartNumber")
    
    def get_memory_dimm_a_channel(self):
        return self.dimm_a.get("DeviceLocator")

    def get_memory_dimm_a_cap(self) -> int:
        memory = self._bytes_converter(int(self.dimm_a.get("Capacity")))
        return memory

    # DIMM B
    def get_memory_dimm_b_manufacturer(self):
        return self.dimm_b.get("Manufacturer")

    def get_memory_dimm_b_model(self):
        return self.dimm_b.get("PartNumber")
    
    def get_memory_dimm_b_channel(self):
        return self.dimm_b.get("DeviceLocator")

    def get_memory_dimm_b_cap(self) -> int:
        memory = self._bytes_converter(int(self.dimm_b.get("Capacity")))
        return memory
    
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
    