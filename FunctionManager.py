import os
import platform

class FileManager:
    def __init__(self, logs_manager):
        self.logs_man = logs_manager

        # Carpeta de LOGS
        self.logs_directory = self.logs_man.op_log_directory
        
        # Atributos
        self.machine_name = platform.node()
        self.db_folder_name = 'DB_List'
        
        # Rutas
        self.db_path = os.path.join(os.getcwd(), self.db_folder_name)

        # Archivos
        self.db_file_name = 'DB_Dictionary.txt'
        
        # Diccionario
        self.dictionary = self.read_db()

    # Esta función lee el diccionario de áreas y crea uno en caso de no haberlo.
    def read_db(self):
        dictionary = {}
        file_path = os.path.join(self.db_path, self.db_file_name)
        try:
            with open(file_path, 'r') as file:
                for items in file.readlines():
                    key, name = items.strip().split(': ')
                    dictionary[key] = name
        except FileNotFoundError as e:
            make_log = (
                f'Falta el directorio de datos DB_Dictionary.txt, se ha generado un README en la ruta {file_path}.\n'
                f'{e}'
            )
            self.logs_man.error_logs_print(self.logs_man.op_log_directory, make_log)
        return dictionary        

    # Crea un diccionario por defecto para su llenado.
    def default_dictionary(self, db_directory, default_file_name):
            file_directory = os.path.join(db_directory, default_file_name)
            try:
                with open(file_directory, 'w') as file:
                    file.write('Crea tu diccionario en este archivo.\n'
                            'NO OLVIDES BORRAR ESTAS DOS LINEAS'
                            )
            except OSError as e:
                make_log = (
                    f'No se pudo generar el archivo de apoyo.\n'
                    f'{e}'                            
                )
                self.logs_man.error_logs_print(self.logs_man.op_log_directory, make_log)

    # Read the device name and compare it with the dictionary to organize the outputs.
    def find_device_area(self, dictionary, code_name):
        # If the device is not recognized in the DB, this will be the default output folder.
        office_folder = 'SIN-ASIGNAR'               # Change this var for your default output folder.

        for lines in dictionary:
            if lines in str(code_name):
                office_folder = dictionary[lines]
                break

        return office_folder
    
class FolderManager:
    def __init__(self, logs_manager):
        self.logs_man = logs_manager
        self.out_folder_name = 'FICHAS'
        self.out_path = os.path.join(os.getcwd(), self.out_folder_name)
        
    def output_path(self):
        self.new_directory(self.out_path)

    # Se encarga de crear nuevos directorios a partir de una dirección de entrada.
    def new_directory(self, new_directory_name):
        try:
            directory = os.path.join(new_directory_name)
            if (os.path.exists(directory) and os.path.isdir(directory)) == False:
                os.mkdir(directory)
        except OSError as e:
            make_log = (f'No se pudo crear el directorio {directory}:'
                       f'{e}'
                       )
            self.logs_man.error_logs_print(self.logs_man.op_log_directory, make_log)