import os
import time


class ScriptManager():
    # This function reads the DB file .txt and fill the empty dictionary with the informatión that you need for organize the output files.
    def read_db(self, db_directory, db_file_name, logs_directory):
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
            self.error_logs_print(logs_directory, err_log)
        return dictionary        

    # Takes the new route and makes the directory.
    def new_directory(self, new_directory_name, logs_directory):
        try:
            directory = os.path.join(new_directory_name)
            if (os.path.exists(directory) and os.path.isdir(directory)) == False:
                os.mkdir(directory)
        except OSError as e:
            err_log = (f'No se pudo crear el directorio {directory}:'
                       f'{e}'
                       )

            self.error_logs_print(logs_directory, err_log)

    def default_dictionary(self, db_directory, default_file_name):
            file_directory = os.path.join(db_directory, default_file_name)
            with open(file_directory, 'w') as file:
                file.write('Crea tu diccionario en este archivo.\n'
                        'NO OLVIDES BORRAR ESTAS DOS LINEAS\n'
                        )

    # Read the device name and compare it with the dictionary to organize the outputs.
    def find_device_area(self, dictionary, code_name):
        # If the device is not recognized in the DB, this will be the default output folder.
        office_folder = 'SIN-ASIGNAR'               # Change this var for your default output folder.

        for lines in dictionary:
            if lines in str(code_name):
                office_folder = dictionary[lines]
                break

        return office_folder

    def error_logs_print(self, logs_directory, error_log):
        date = str(time.strftime('%d-%m-%Y_%H-%M-%S'))
        log_name = f'E_LOG - {date}.txt'
        if (os.path.exists(logs_directory) and os.path.isdir(logs_directory)) == False:
            self.new_directory(logs_directory, logs_directory)
        else:
            new_directory = os.path.join(logs_directory, log_name)
        
            with open(new_directory, 'w') as file:
                file.write(error_log)