import os
import platform
import psutil
import socket
import subprocess
import re

class SystemInformationCatcher:
    def __init__(self, logs_manager):
        self.logs_man = logs_manager
        
        self.machine_mac = self.MachineMAC()
        self.machine_id = self.MachineID()
        self.machine_name = platform.node()                   
        self.machine_ip = self.IpCatcher()
        self.machine_ram, _, _, _, _, = psutil.virtual_memory()
        self.machine_disk, _, _, _, = psutil.disk_usage('C:\\')
        self.machine_mark = self.MoboManufInfo()
        self.machine_mobo = self.MoboModelInfo()
        self.machine_cpu = self.CpuNameInfo()
        self.os_product = self.WinProduct()
        self.os_arch = self.WinArch()
        self.user_acc_name = os.getlogin()
        self.user_dom_name = self.HostNameInfo()
        self.soft_anydesk = self.anydeskid()

    # Ejecuta y limpia los comandos.
    def CommandExecution(self, command_line):
        Command_Process = subprocess.getoutput(command_line).split('\n')
        self.result = Command_Process[2].strip()
        return self.result

    # Convierte bits a bytes.
    def BytesConverter(self, total_Bytes):
        return total_Bytes / (1024 ** 3)

    # Comprueba el registro a un dominio, en caso de no haber uno, coloca el grupo al que esta registrado.
    def HostNameInfo(self):
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
    
    # Obtiene la direccion IP del adaptador Ethernet principal.
    def IpCatcher(self):
        ip_format = re.compile(r'\b\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\b')
        Command_Args = ['netsh', 'interface', 'ipv4', 'show', 'ipaddresses', 'Ethernet']
        self.machine_ip = subprocess.getoutput(Command_Args).split()
        for items in self.machine_ip:
            ip_match = ip_format.fullmatch(items)
            if ip_match:
                self.machine_ip = ip_match.group()
                break

        return self.machine_ip

    # Obtiene la direccion MAC del equipo.
    def MachineMAC(self):
        Command_Args = ['wmic', 'nic', 'get', 'MACAddress']
        output = subprocess.getoutput(Command_Args).split('\n')
        cleaned_list = [index.strip() for index in output if index.strip()]
        self.machine_mac = cleaned_list[1]

        return self.machine_mac 

    # Obtiene el ID de Windows que identifica el equipo, este cambia en cada formateo del equipo.
    def MachineID(self):
        key_directory = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\SQMClient'
        try:
            CommandOut = subprocess.getoutput(['reg', 'query', f'{key_directory}', '/v', 'MachineId']).split('\n')[1:-1]
        except Exception as e:
            make_log = (
                f'Ocurrio un error durante la busqueda del ID del dispositivo.\n'
                f'{e}\n'   
            )
            self.logs_man.error_logs_print(self.logs_man.op_log_directory, make_log)

        searchData = re.search(r'{(.*?)}', CommandOut[1])
        self.machine_id = searchData.group(1)
        return self.machine_id

    def MoboModelInfo(self):
        Command_Args = ['wmic', 'baseboard', 'get', 'product']
        self.CommandExecution(Command_Args)
        self.ProductModel = self.result
        return self.ProductModel
    
    def MoboManufInfo(self):
        Command_Args = ['wmic', 'baseboard', 'get', 'manufacturer']
        self.CommandExecution(Command_Args)
        self.MoboManufacturer = self.result
        return self.MoboManufacturer

    def CpuNameInfo(self):
        Command_Args = ['wmic', 'cpu', 'get', 'name']
        self.CommandExecution(Command_Args)
        self.cpu_name = self.result
        return self.cpu_name
    
    def WinProduct(self):
        Command_Args = ['wmic', 'os', 'get', 'caption']
        self.CommandExecution(Command_Args)
        self.os_product = self.result
        return self.os_product
    
    def WinArch(self):
        Command_Args = ['wmic', 'os', 'get', 'osarchitecture']
        self.CommandExecution(Command_Args)
        self.os_arch = self.result
        return self.os_arch
    
    def anydeskid(self):
        folder_route = f'C:/Users/{self.user_acc_name}/AppData/Roaming/'
        folder_name = 'AnyDesk'
        complete_directory = os.path.join(folder_route, folder_name)
        file_name = 'system.conf'
        
        # IF#1 Comprueba la existencia del directorio principal de Anydesk.
        # IF#2 Comprueba la existencia del archivo que deberia contener el ID de estacion.
        if os.path.exists(complete_directory) and os.path.isdir(complete_directory):
            id_search = os.path.join(complete_directory, file_name)
            if os.path.exists(id_search) and os.path.isfile(id_search):
                with open(id_search, 'r') as file:
                        for items in file.readlines():
                                if '.id=' in items:
                                    self.soft_anydesk = items.split('=')[1][:-1]
                                    return self.soft_anydesk
                        else:
                            make_log = (
                                f'El ID de escritorio no se encuentra dentro de {file_name}.\n'
                                f'Desinstala y reinstala Anydesk para reparar este error.'
                                )
                            self.logs_man.error_logs_print(self.logs_man.op_log_directory, make_log)
                            return 'Revisa el ERROR_LOG...'
            else:
                return 'Reinstalar AnyDesk.'
        else:
            return 'Instala AnyDesk.'
    
    # Genera una formato de salida con la informacion obtenida en los atributos de la clase.
    def PrintInfo(self):
        output = (
            f'Nombre del equipo: {self.machine_name}\n'
            f'Nombre de la cuenta: {self.user_acc_name}\n' 
            f'Nombre de usuario en el dominio: {self.user_dom_name}\n'
            f'ID del equipo: {self.machine_id} || MAC: {self.machine_mac}\n'
            f'Marca del equipo: {self.machine_mark}\n'
            f'Procesador: {self.machine_cpu}\n'
            f'Memoria RAM: {round(self.BytesConverter(self.machine_ram),0)} GB\n'
            f'Motherboard: {self.machine_mobo}\n'
            f'Almacenamiento: {round(self.BytesConverter(self.machine_disk),0)} GB\n'
            f'Direccion IP: {self.machine_ip}\n'
            f'Sistema Operativo: {self.os_product} {self.os_arch}\n'
            f'AnyDesk ID: {self.soft_anydesk}'
        )
        
        with open(f'{self.machine_name}.txt','w') as file:
            file.write(output)