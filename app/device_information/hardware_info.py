import subprocess

from psutil import disk_usage, virtual_memory

class HardwareInfo:
    # Convierte bits a bytes.
    def _bytes_converter(self, total_Bytes):
        return total_Bytes / (1024 ** 3)
    
    # Ejecuta comandos y entrega la salida como string.
    def execute_command(self, command=str):
        return subprocess.getoutput(command)
    
    # PROCESADOR
    # Obtiene el nombre completo y datos principales del CPU.
    def get_cpu_model(self):
        output = self.execute_command('wmic cpu get name').split('\n')
        cpu_model = [line.strip()for line in output if line.strip()][1]
        return cpu_model
    
    # MEMORIA RAM
    # Obtiene la capacitad total disponible en memoria RAM.
    def get_total_memory_ram(self):
        totalMemory = virtual_memory().total
        systemMemory = f"{round(self._bytes_converter(totalMemory), 0)} GB"
        return systemMemory
    
    # MOTHERBOARD
    # Obtiene el modelo del Motherboard    
    def get_motherboard_model(self):
        output = self.execute_command('wmic baseboard get product').split('\n')
        mobo_model = [line.strip()for line in output if line.strip()][1]
        return mobo_model
    
    # Obtiene el nombre del fabricante del Motherboard.
    def get_motherboard_manufacturer(self):
        output = self.execute_command('wmic baseboard get manufacturer').split('\n')
        mobo_manuf = [line.strip()for line in output if line.strip()][1]
        return mobo_manuf
    
    # ALMACENAMIENTO PRINCIPAL
    def get_main_storage(self):
        # Obtiene el modelo de la unidad de almacenamiento principal.
        def _get_disk_model():
            output = self.execute_command("wmic diskdrive where index=0 get model /all").split('\n')
            disk_model = [line.strip()for line in output if line.strip()][1]
            return disk_model
    
        # Obtiene la capacidad total del disco principal
        def _get_storage_cap():
            totalStorage = disk_usage("C:\\").total
            systemStorage = f"{round(self._bytes_converter(totalStorage), 0)} GB"
            return systemStorage
        
        return f"{_get_storage_cap()} {_get_disk_model()}"
    