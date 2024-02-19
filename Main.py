import os
import time

from SystemInfoCapture import SystemInformationCatcher
from Readme_Write import Readme

# This function reads the DB file .txt and fill the empty dictionary with the informatión that you need for organize the output files.
def read_db(directory, file_name):
    dictionary = {}
    file_directory = os.path.join(directory, file_name)
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
        error_logs_print(err_log)
    return dictionary        

# Takes the new route and makes the directory.
def new_directory(current_directory, input_directory):
    try:
        directory = os.path.join(current_directory, input_directory)
        if (os.path.exists(directory) and os.path.isdir(directory)) == False:
            os.mkdir(directory)
    except OSError as e:
        err_log = f'No se pudo crear el directorio {directory}: {e}'
        error_logs_print(err_log)

# Read the device name and compare it with the dictionary to organize the outputs.
def find_device_area(dictionary, code_name):
    # If the device is not recognized in the DB, this will be the default output folder.
    office_folder = 'DESCONOCIDO'               # Change this var for your default output folder.

    for lines in dictionary:
        if lines in str(code_name):
            office_folder = dictionary[lines]
            break

    return office_folder

def make_logs_folder(directory, logs_folder):
    logs_directory = os.path.join(directory, logs_folder)
    if (os.path.exists(logs_directory) and os.path.isdir(logs_directory)) == False:
        new_directory(logs_directory)
    else:
        return logs_directory

def error_logs_print(directory, logs_folder, error_log):
    date = str(time.strftime('%d-%m-%Y_%H-%M-%S'))
    log_name = f'E_LOG - {date}.txt'
    error_directory = os.path.join(make_logs_folder(directory, logs_folder), log_name)
    
    with open(error_directory, 'w') as file:
        file.write(error_log)
    

# Main function
def execute_program():
    # Hashtag (jaja)
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
    file_name = 'DB_Dictionary.txt'

    if os.path.exists(complete_directory) and os.path.isdir(complete_directory):
        read_db(complete_directory, file_name)
        output_route = find_device_area(read_db(), code_name)
        new_directory(script_directory, output_route)    
        os.chdir(output_route)
        device_name.PrintInfo()
    else:
        new_directory(complete_directory)
        try:
            readme_file = os.path.join(complete_directory, 'README.txt')
            with open(readme_file, 'w') as file:
                file.write(help_file.write_txt_readme)
        except Exception as e:
            err_log = f'No se pudo generar el archivo de apoyo. {e}'
            error_logs_print(logs_directory, logs_folder, err_log)

execute_program()