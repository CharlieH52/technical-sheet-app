import os
import platform
import psutil
import socket
import subprocess

class SystemInformationCatcher:
    def __init__(self):
        self.machine_id = self._MachineID()
        self.machine_name = platform.node()                   
        self.machine_ip = socket.gethostbyname(self.machine_name)
        self.machine_ram, _, _, _, _, = psutil.virtual_memory()
        self.machine_disk, _, _, _, = psutil.disk_usage('C:\\')
        self.machine_mark = self._MoboManufInfo()
        self.machine_mobo = self._MoboModelInfo()
        self.machine_cpu = self._CpuNameInfo()
        self.os_product = self._WinProduct()
        self.os_arch = self._WinArch()
        self.user_acc_name = os.getlogin()
        self.user_dom_name = self._HostNameInfo()
        self.soft_anydesk = self._anydeskid()
    
    # Bytes converter
    def _BytesConverter(self, total_Bytes):
        return total_Bytes / (1024 ** 3)

    # Search for a domain addres, if the system has't a domain...
    # Execute the CMD code 'Systeminfo' then clean the output and gives the GroupName.
    def _HostNameInfo(self):
        HostName = socket.gethostbyaddr(self.machine_name)[1]
        if HostName == []:
            CommandOut = subprocess.getoutput('systeminfo').split('\n')[1:-1]
            SearchData = 'Dominio'
            for lineItem in CommandOut:
                if SearchData in lineItem:
                    self.FOutput = f'{self.machine_name}.{(lineItem.split(':')[1]).strip()}'
        else:
            self.FOutput = HostName
        
        return self.FOutput
    
    # Search and consult a specific registry key for obtain Machine ID.
    def _MachineID(self):
        keyRute = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\SQMClient'
        CommandOut = subprocess.getoutput(['reg', 'query', f'{keyRute}', '/v', 'MachineId']).split('\n')[1:-1]
        SearchData = '-'
        for linesID in CommandOut:
            if SearchData in linesID:
                self.machineid = linesID.split()
                for SData in self.machineid:
                    if SearchData in SData:
                        self.machineid = SData.strip('{')
                        self.machineid = self.machineid.strip('}')

        return self.machineid    

    # Use the input command and clean the output for post use
    def _CommandExecution(self, command_line):
        Command_Process = subprocess.getoutput(command_line).split('\n')
        self.result = Command_Process[2].strip()
        return self.result

    def _MoboModelInfo(self):
        Command_Args = ['wmic', 'baseboard', 'get', 'product']
        self._CommandExecution(Command_Args)
        self.ProductModel = self.result
        return self.ProductModel
    
    def _MoboManufInfo(self):
        Command_Args = ['wmic', 'baseboard', 'get', 'manufacturer']
        self._CommandExecution(Command_Args)
        self.MoboManufacturer = self.result
        return self.MoboManufacturer

    def _CpuNameInfo(self):
        Command_Args = ['wmic', 'cpu', 'get', 'name']
        self._CommandExecution(Command_Args)
        self.cpu_name = self.result
        return self.cpu_name
    
    def _WinProduct(self):
        Command_Args = ['wmic', 'os', 'get', 'caption']
        self._CommandExecution(Command_Args)
        self.os_product = self.result
        return self.os_product
    
    def _WinArch(self):
        Command_Args = ['wmic', 'os', 'get', 'osarchitecture']
        self._CommandExecution(Command_Args)
        self.os_arch = self.result
        return self.os_arch
    
    def _anydeskid(self):
        folder_route = f'C:/Users/{self.user_acc_name}/AppData/Roaming/'
        folder_name = 'AnyDesk'
        complete_directory = os.path.join(folder_route, folder_name)
        file_name = 'system.conf'
        
        if os.path.exists(complete_directory) and os.path.isdir(complete_directory):
            id_search = os.path.join(complete_directory, file_name)
            if os.path.exists(id_search) and os.path.isfile(id_search):
                with open(id_search, 'r') as file:
                    for items in file.readlines():
                        if '.id=' in items:
                            self.soft_anydesk = items.split('=')[1]
            else:
                output_message = 'AnyDesk no instalado.'
                self.soft_anydesk = output_message
        
        return self.soft_anydesk
    
    # Save very data in his respective variable space and print it.
    def PrintInfo(self):
        output = (
        f'Nombre del equipo: {self.machine_name}\n'
        f'Nombre de la cuenta: {self.user_acc_name}\n' 
        f'Nombre de usuario en el dominio: {self.user_dom_name}\n'
        f'ID del dispositivo: {self.machine_id}\n'
        f'Marca del equipo: {self.machine_mark}\n'
        f'Procesador: {self.machine_cpu}\n'
        f'Memoria RAM: {round(self._BytesConverter(self.machine_ram),0)} GB\n'
        f'Motherboard: {self.machine_mobo}\n'
        f'Almacenamiento: {round(self._BytesConverter(self.machine_disk),0)} GB\n'
        f'Direccion IP: {self.machine_ip}\n'
        f'Sistema Operativo: {self.os_product} {self.os_arch}\n'
        f'AnyDesk ID: {self.soft_anydesk}\n'
        )
        
        with open(f'{self.machine_name}.txt','w') as file:
            file.write(output)
