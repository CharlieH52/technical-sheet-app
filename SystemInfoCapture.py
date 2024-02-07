import os
import platform
import psutil
import socket
import subprocess

class SysData:
    def __init__(self):
        self.machine_id = self.MachineID()
        self.machine_name = platform.node()                   
        self.machine_ip = socket.gethostbyname(self.machine_name)
        self.machine_ram, _, _, _, _, = psutil.virtual_memory()
        self.machine_disk, _, _, _, = psutil.disk_usage("C:\\")
        self.machine_mark = self.MoboManufInfo()
        self.machine_mobo = self.MoboModelInfo()
        self.machine_cpu = self.CpuNameInfo()
        self.os_product = self.WinProduct()
        self.os_arch = self.WinArch()
        self.user_acc_name = os.getlogin()
        self.user_dom_name = self.HostNameInfo()
    
    def BytesConverter(self, total_Bytes):
        return total_Bytes / (1024 ** 3)

    # Search for a domain addres, if the system has't a domain...
    # Execute the CMD code "Systeminfo" then clean the output and gives the GroupName.
    def HostNameInfo(self):
        HostName = socket.gethostbyaddr(self.machine_name)[1]
        if HostName == []:
            CommandOut = subprocess.getoutput('systeminfo').split('\n')[1:-1]
            SearchData = "Dominio"
            for lineItem in CommandOut:
                if SearchData in lineItem:
                    self.FOutput = f"{self.machine_name}.{(lineItem.split(':')[1]).strip()}"
            return self.FOutput
        else:
            self.FOutput = print(f"Var Host: {HostName}")
            return self.FOutput
    
    # 
    def MachineID(self):
        keyRute = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\SQMClient"
        CommandOut = subprocess.getoutput(['reg', 'query', f'{keyRute}', '/v', 'MachineId']).split('\n')[1:-1]
        self.machineid = CommandOut
        SearchData = "-"
        for linesID in CommandOut:
            if SearchData in linesID:
                self.machineid = linesID.split()
                for SData in self.machineid:
                    if SearchData in SData:
                        self.machineid = SData.strip('{')
                        self.machineid = self.machineid.strip('}')

        return self.machineid    

    def MoboModelInfo(self):
        CommandOut = subprocess.run(['wmic', 'baseboard', 'get', 'product'], capture_output=True, text=True)
        OutResult = CommandOut.stdout

        InfLines = OutResult.split('\n')
        self.ProductModel = InfLines[2].strip()
        return self.ProductModel
    
    def MoboManufInfo(self):
        CommandOut = subprocess.run(['wmic', 'baseboard', 'get', 'manufacturer'], capture_output=True, text=True)
        OutResult = CommandOut.stdout

        InfLines = OutResult.split('\n')
        self.ManufInfo = InfLines[2].strip()
        return self.ManufInfo

    def CpuNameInfo(self):
        CommandOut = subprocess.run(['wmic', 'cpu', 'get', 'name'], capture_output=True, text=True)
        OutResult = CommandOut.stdout

        InfLines = OutResult.split('\n')
        self.cpu_name = InfLines[2].strip()
        return self.cpu_name
    
    def WinProduct(self):
        CommandOut = subprocess.run(['wmic', 'os', 'get', 'caption'], capture_output=True, text=True)
        OutResult = CommandOut.stdout

        InfLines = OutResult.split('\n')
        self.os_product =InfLines[2].strip()
        return self.os_product
    
    def WinArch(self):
        CommandOut = subprocess.run(['wmic', 'os', 'get', 'osarchitecture'], capture_output=True, text=True)
        OutResult = CommandOut.stdout

        InfLines = OutResult.split('\n')
        self.os_arch =InfLines[2].strip()
        return self.os_arch


    def PrintInfo(self):
        try:
            output = (
            f"Nombre del equipo: {self.machine_name}\n"
            f"Nombre de la cuenta: {self.user_acc_name}\n" 
            f"Nombre de usuario en el dominio: {self.user_dom_name}\n"
            f"ID del dispositivo: {self.machine_id}\n"
            f"Marca del equipo: {self.machine_mark}\n"
            f"Procesador: {self.machine_cpu}\n"
            f"Memoria RAM: {round(self.BytesConverter(self.machine_ram),0)} GB\n"
            f"Motherboard: {self.machine_mobo}\n"
            f"Almacenamiento: {round(self.BytesConverter(self.machine_disk),0)} GB\n"
            f"Dirección IP: {self.machine_ip}\n"
            f"Sistema Operativo: {self.os_product} {self.os_arch}\n"
            )
            print(output)
        except Exception as e:
            print("ERROR: No se pudo obtener la información solicitada...")
        try:
            with open(f"{self.machine_name}.txt","w") as file:
                file.write(output)
        except Exception as e:
            print("ERROR: No se puedo generar el archivo de salida...")
