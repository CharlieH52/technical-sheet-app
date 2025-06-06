import subprocess

from psutil import disk_usage, virtual_memory

class HardwareInfo:
    # bits to bytes converter.
    def _bytes_converter(self, total_Bytes):
        return total_Bytes / (1024 ** 3)
    
    # Execute commands and get back the output as string.
    def execute_command(self, command=str):
        return subprocess.getoutput(command)
    
    # CPU
    # Obtain the full name and the main specs about the processor.
    def get_cpu_model(self):
        output = self.execute_command('wmic cpu get name').split('\n')
        cpu_model = [line.strip()for line in output if line.strip()][1]
        return cpu_model
    
    # MEMORY RAM
    # Obtain the memory cap of the installed memory.
    def get_total_memory_ram(self):
        totalMemory = virtual_memory().total
        systemMemory = f"{round(self._bytes_converter(totalMemory), 0)} GB"
        return systemMemory
    
    # MOTHERBOARD
    # Obtain the model name. 
    def get_motherboard_model(self):
        output = self.execute_command('wmic baseboard get product').split('\n')
        mobo_model = [line.strip()for line in output if line.strip()][1]
        return mobo_model
    
    # Obtain the name of the manufacturer.
    def get_motherboard_manufacturer(self):
        output = self.execute_command('wmic baseboard get manufacturer').split('\n')
        mobo_manuf = [line.strip()for line in output if line.strip()][1]
        return mobo_manuf
    
    # MAIN STORAGE
    # Obtain the model name of the main storage device.
    def _get_disk_model(self):
        output = self.execute_command("wmic diskdrive where index=0 get model /all").split('\n')
        disk_model = [line.strip()for line in output if line.strip()][1]
        return disk_model

    # Obtain the memory cap of the main storage device.
    def _get_storage_cap(self):
        totalStorage = disk_usage("C:\\").total
        systemStorage = f"{round(self._bytes_converter(totalStorage), 0)} GB"
        return systemStorage
    
    # Get the full data about the main storage device.
    def get_main_storage(self):
        return f"{self._get_storage_cap()} {self._get_disk_model()}"
    