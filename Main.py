import os

from SystemInfoCapture import SystemInformationCatcher
from Readme_Write import Readme

insSysData = SystemInformationCatcher()
HelpFile = Readme()

script_directory = os.getcwd()
db_folder = "DB_List"
office_folder = ""
new_folder = insSysData.machine_name 
complete_directory = os.path.join(script_directory, db_folder)
file_name = "DB_Dictionary.txt"
dictionary = {}

def _read_db():
    file_directory = os.path.join(complete_directory, file_name)
    try:
        with open(file_directory, 'r') as file:
            for items in file.readlines():
                key, name = items.strip().split(': ')
                dictionary[key] = name
    except FileNotFoundError:
        print('No se encontro el archivo DB_Dictionary.txt')

    except Exception as e:
        print(f'No se pudo abrir el archivo. {e}')        

def _new_directory(route):
    office_rute = os.path.join(script_directory, route)
    if (os.path.exists(office_rute) and os.path.isdir(office_rute)) == False:
        os.mkdir(office_rute)

def _find_device_area():
    office_folder = "DESCONOCIDO"

    for index in dictionary:
        if index in str(new_folder):
            office_folder = dictionary[index]
            break

    return office_folder

def execute_program():
    try:
        if os.path.exists(complete_directory) and os.path.isdir(complete_directory):
            _read_db()                                                                       # Open and read the DB_File.
            try:
                output_route = _find_device_area()                                           # Save the path for the next use.
                _new_directory(output_route)                                                 # Makes the directory with the name area using the key in the device name if this exist.    
            except Exception as e:
                print(f'Ocurrio un problema al crear el directorio. {e}')

            os.chdir(output_route)                                                          # Change the working path.
            insSysData.PrintInfo()                                                          # write the file with all device information.
        else:
            _new_directory(complete_directory)
            try:
                readme_file = os.path.join(complete_directory, "README.txt")
                with open(readme_file, 'w') as file:
                    file.write(HelpFile.write_txt_readme)
            except Exception as e:
                print(f'No se pudo generar el archivo de apoyo. {e}')
    except Exception as e:
        print(f'No se ha encontrado la ruta "\\DB_List", favor de crear el directorio. {e}')

execute_program()