import os

from SystemCatcher import SystemInformationCatcher
from FunctionManager import *
from LogManager import LogManagerSystem

if __name__ == '__main__':
    PRODUCTION_MODE = True
    logs_man = LogManagerSystem()
    device_name = SystemInformationCatcher(logs_man)
    fold_man = FolderManager(logs_man)
    file_man = FileManager(logs_man)

    if PRODUCTION_MODE == True:
        key_name = device_name.machine_name

        # Crea el directorio de 'LOGS'
        fold_man.new_directory(logs_man.op_log_directory)

        if os.path.isdir(fold_man.out_path) == False:
            fold_man.output_path()

        if os.path.isdir(file_man.db_path) == True:
            output_route = os.path.join(fold_man.out_path, file_man.find_device_area(file_man.dictionary, key_name))
            fold_man.new_directory(output_route)    
            os.chdir(output_route)
            device_name.PrintInfo()
        else:
            file_man.default_dictionary(file_man.db_path, file_man.db_file_name)

    else:
        def run_test():
            # Inserta aqui el codigo a probar...
            print('ESTAS EJECUTANDO EL MODO DE PRUEA\n')

        run_test()