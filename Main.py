import os

from SystemCatcher import SystemInformationCatcher
from FunctionManager import *
from LogManager import LogManagerSystem

# Main function
def execute_program():
    logs_man = LogManagerSystem()
    device_name = SystemInformationCatcher(logs_man)
    fold_man = FolderManager(logs_man)
    file_man = FileManager(logs_man)
    
    key_name = device_name.machine_name
    
    # Crea el directorio de 'LOGS'
    fold_man.new_directory(logs_man.op_log_directory)
    
    if os.path.exists(file_man.db_path) and os.path.isdir(file_man.db_path):
        output_route = os.path.join(os.getcwd(), file_man.find_device_area(file_man.dictionary, key_name))
        fold_man.new_directory(output_route)    
        os.chdir(output_route)
        device_name.PrintInfo()
    else:
        file_man.default_dictionary(file_man.db_path, file_man.db_file_name)

if __name__ == '__main__':
    execute_program()
    