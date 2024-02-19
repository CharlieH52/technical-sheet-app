import os
import time

from SystemInfoCapture import SystemInformationCatcher
from Readme_Write import Readme

# This function reads the DB file .txt and fill the empty dictionary with the informatión that you need for organize the output files.
def read_db(db_directory, db_file_name, logs_directory):
    dictionary = {}
    file_directory = os.path.join(db_directory, db_file_name)
    try:
        with open(file_directory, 'r') as file:
            for items in file.readlines():
                key, name = items.strip().split(': ')
                dictionary[key] = name
    except FileNotFoundError as e:
        err_log = (
            f'Falta el directorio de datos DB_Dictionary.txt, se ha generado un README en la ruta {file_directory}.\n'
            f'{e}\n'
        )
        error_logs_print(logs_directory, err_log)
    return dictionary        

# Takes the new route and makes the directory.
def new_directory(new_directory_name, logs_directory):
    try:
        directory = os.path.join(new_directory_name)
        if (os.path.exists(directory) and os.path.isdir(directory)) == False:
            os.mkdir(directory)
    except OSError as e:
        err_log = f'No se pudo crear el directorio {directory}: {e}'
        error_logs_print(logs_directory, err_log)

def default_dictionary(db_directory, default_file_name):
        file_directory = os.path.join(db_directory, default_file_name)
        with open(file_directory, 'w') as file:
            file.write('Crea tu diccionario en este archivo.\n'
                       'NO OLVIDES BORRAR ESTAS DOS LINEAS\n'
                       )

# Read the device name and compare it with the dictionary to organize the outputs.
def find_device_area(dictionary, code_name):
    # If the device is not recognized in the DB, this will be the default output folder.
    office_folder = 'SIN-ASIGNAR'               # Change this var for your default output folder.

    for lines in dictionary:
        if lines in str(code_name):
            office_folder = dictionary[lines]
            break

    return office_folder

def error_logs_print(logs_directory, error_log):
    date = str(time.strftime('%d-%m-%Y_%H-%M-%S'))
    log_name = f'E_LOG - {date}.txt'
    if (os.path.exists(logs_directory) and os.path.isdir(logs_directory)) == False:
        new_directory(logs_directory)
    else:
        logs_directory = os.path.join(logs_directory, log_name)
    
        with open(logs_directory, 'w') as file:
            file.write(error_log)

# Main function
def execute_program():
    device_name = SystemInformationCatcher()
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

    if os.path.exists(complete_directory) and os.path.isdir(complete_directory):
        dictionary = read_db(complete_directory, db_file_name, logs_directory)
        output_route = os.path.join(script_directory, find_device_area(dictionary, code_name))
        new_directory(output_route, logs_directory)    
        os.chdir(output_route)
        device_name.PrintInfo()
    else:
        new_directory(complete_directory, logs_directory)
        default_dictionary(complete_directory, db_file_name)
        try:
            readme_file = os.path.join(logs_directory, readme_file_name)
            with open(readme_file, 'w') as file:
                file.write(help_file.write_txt_readme)
        except Exception as e:
            err_log = f'No se pudo generar el archivo de apoyo. {e}'
            error_logs_print(logs_directory, err_log)

execute_program()