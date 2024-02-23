import os

from SystemInfoCapture import SystemInformationCatcher
from FileFunctions import ScriptManager
from Readme_Write import Readme

# Linea de compilación:
# COPY: pyinstaller --clean --windowed --onefile --distpath="D:\Documentos\Portfoil-Programacion\OUTPUT-FILES\GENERADOR-TECNICO" --name=Generar-Ficha-x64 Main.py

# Main function
def execute_program():
    device_name = SystemInformationCatcher()
    manager = ScriptManager()
    help_file = Readme()

    # Directories
    script_directory = os.getcwd()
    db_folder = 'DB_List'
    logs_folder = 'LOGS'
    code_name = device_name.machine_name
    complete_directory = os.path.join(script_directory, db_folder)
    logs_directory = os.path.join(script_directory, logs_folder)
    
    # File names
    db_file_name = 'DB_Dictionary.txt'
    readme_file_name = 'README.txt'

    # Make the LOGS folder
    manager.new_directory(logs_directory, logs_directory)
    
    if os.path.exists(complete_directory) and os.path.isdir(complete_directory):
        dictionary = manager.read_db(complete_directory, db_file_name, logs_directory)
        output_route = os.path.join(script_directory, manager.find_device_area(dictionary, code_name))
        manager.new_directory(output_route, logs_directory)    
        os.chdir(output_route)
        device_name.PrintInfo()
    else:
        try:
            manager.default_dictionary(complete_directory, db_file_name)
            readme_file = os.path.join(complete_directory, readme_file_name)
            with open(readme_file, 'w') as file:
                file.write(help_file.write_txt_readme)
        except Exception as e:
            err_log = f'No se pudo generar el archivo de apoyo. {e}'
            manager.error_logs_print(logs_directory, err_log)

execute_program()