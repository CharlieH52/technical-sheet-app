import os
import subprocess
import re

class SystemInfo:
    # Ejecuta comandos y entrega la salida como string.
    def _execute_command(self, command=str):
        return subprocess.getoutput(command)

    # Obtiene el nombre de la cuenta de usuario.
    # Se necesita refactorizar este bloque por algo mas sencillo.
    def get_system_user_name(self):
        regEx = r"^[^\w]*[A-Z]+\\[A-Z]+\s*"
        try:
            user_list = self._execute_command("wmic useraccount get fullname, caption").split('\n')
            for users in user_list:
                if os.getlogin() in users:
                    system_user = re.sub(regEx, ' ', users).strip()
            return system_user
        except Exception:
             return None
    
    def win_product(self):
        output = self._execute_command("wmic os get caption").split('\n')
        product = [line.strip()for line in output if line.strip()][1]
        return product
    
    # Obtiene la arquitectura del SO instalado.
    def win_architecture(self):
        output = self._execute_command("wmic os get osarchitecture").split('\n')
        bits = [line.strip()for line in output if line.strip()][1]
        return bits
    
    # Obtiene la version del producto Windows instalado en el sistema.
    def get_windows_version(self):
        return (f"{self.win_product()} {self.win_architecture()}")