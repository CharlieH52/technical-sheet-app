import os
import platform
import psutil
import socket
import subprocess
import re

class SystemInformationCatcher:
    def __init__(self, logs_manager):
        self.logs_man = logs_manager
        
        self.machine_mac = self.machine_mac_add()
        #self.machine_id = self.machine_id_num()
        self.machine_name = platform.node()                   
        self.machine_ip = self.ip_address_catcher()
        self.machine_disk, _, _, _, = psutil.disk_usage('C:\\')
        self.machine_memory, _, _, _, _, = psutil.virtual_memory()
        self.machine_disk_model = self.disk_model()
        self.machine_mark = self.mobo_manuf_info()
        self.machine_mobo = self.mobo_model_info()
        self.machine_cpu = self.cpu_name_info()
        self.os_product = self.win_product()
        self.os_arch = self.win_architecture()
        self.user_acc_name = os.getlogin()
        self.user_dom_name = self.domain_checker()
        self.soft_anydesk = self.anydesk_id_checker()

    def command_execute(self, command_line, option):
        command_process = subprocess.getoutput(command_line).split('\n')
        if option == 0:
            output = command_process
            return output

        # Para salidas normales cortas
        if option == 1:
            output = [item.strip() for item in command_process if item.strip()]
            return output[1]    

    # Convierte bits a bytes.
    def BytesConverter(self, total_Bytes):
        return total_Bytes / (1024 ** 3)

    # Comprueba el registro a un dominio, en caso de no haber uno, coloca el grupo al que esta registrado.
    def domain_checker(self):
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
    def ip_address_catcher(self):
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
    def machine_mac_add(self):
        Command_Args = ['wmic', 'nic', 'get', 'MACAddress']
        output = self.command_execute(Command_Args, 1)
        return output

    # Obtiene el ID de Windows que identifica el equipo, este cambia en cada formateo del equipo.
    def machine_id_num(self):
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

    # Obtiene el modelo del Motherboard    
    def mobo_model_info(self):
        Command_Args = ['wmic', 'baseboard', 'get', 'product']
        output = self.command_execute(Command_Args, 1)
        return output
    
    # Obtiene el nombre del fabricante del Motherboard.
    def mobo_manuf_info(self):
        Command_Args = ['wmic', 'baseboard', 'get', 'manufacturer']
        output = self.command_execute(Command_Args, 1)
        return output
    
    # Obtiene el modelo de la unidad de almacenamiento principal.
    def disk_model(self):
        command_args = ['wmic', 'diskdrive', 'where', 'index = 0', 'get', 'model', '/all']
        output = self.command_execute(command_args, 1)
        return output

    # Obtiene el nombre completo y datos principales del CPU.
    def cpu_name_info(self):
        Command_Args = ['wmic', 'cpu', 'get', 'name']
        output = self.command_execute(Command_Args, 1)
        return output
    
    # Obtiene la version del producto Windows instalado en el sistema.
    def win_product(self):
        Command_Args = ['wmic', 'os', 'get', 'caption']
        output = self.command_execute(Command_Args, 1)
        return output
    
    # Obtiene la arquitectura del SO instalado.
    def win_architecture(self):
        Command_Args = ['wmic', 'os', 'get', 'osarchitecture']
        output = self.command_execute(Command_Args, 1)
        return output

    # Obtiene el ID de escritorio de AnyDesk.
    def anydesk_id_checker(self):
        folder_route = f'C:/Users/{self.user_acc_name}/AppData/Roaming/'
        folder_name = 'AnyDesk'
        complete_directory = os.path.join(folder_route, folder_name)
        file_name = 'system.conf'
        
        # IF#1 Comprueba la existencia del directorio principal de Anydesk.
        # IF#2 Comprueba la existencia del archivo que deberia contener el ID de estacion.
        if os.path.isdir(complete_directory) == True:
            id_search = os.path.join(complete_directory, file_name)
            if os.path.isfile(id_search) == True:
                with open(id_search, 'r') as file:
                        for items in file.readlines():
                                if '.id=' in items:
                                    self.soft_anydesk = items.split('=')[1][:-1]
                                    return self.soft_anydesk
                        else:
                            make_log = (
                                f'El ID de escritorio no se encuentra dentro de {file_name}.\n'
                                f'Desinstala y reinstala Anydesk para solucionar este error.'
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
            f'OfficeName: {self.machine_name}\n'
            f'DeviceName: {self.user_acc_name}\n' 
            f'AccountName: {self.user_dom_name}\n'
            f'UserDomain: {self.machine_mac}\n'
            f'MACAdd: {self.machine_mark}\n'
            f'CPU: {self.machine_cpu}\n'
            f'MemRAM: {round(self.BytesConverter(self.machine_memory),0)} GB\n'
            f'MOBO: {self.machine_mobo}\n'
            f'Storage: {round(self.BytesConverter(self.machine_disk),0)} GB {self.machine_disk_model}\n'
            f'IPAdd: {self.machine_ip}\n'
            f'OSName: {self.os_product} {self.os_arch}\n'
            f'AnyDeskID: {self.soft_anydesk}'
        )
        
        with open(f'{self.machine_name}.txt','w') as file:
            file.write(output)