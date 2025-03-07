import os
import subprocess
import re

from app.shared.error_messages import ERROR_PRINTS

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
    
    def get_windows_version(self):
        # Obtiene la version del producto Windows instalado en el sistema.
        def _win_product():
            output = self._execute_command("wmic os get caption").split('\n')
            product = [line.strip()for line in output if line.strip()][1]
            return product
        
        # Obtiene la arquitectura del SO instalado.
        def _win_architecture():
            output = self._execute_command("wmic os get osarchitecture").split('\n')
            bits = [line.strip()for line in output if line.strip()][1]
            return bits
        
        return (f"{_win_product()} {_win_architecture()}")