import pandas as pd

from src.google_connect.google_actions import GoogleSheet
from src.device_information.anydesk_info import AnyDeskInfo
from src.device_information.hardware_info import HardwareInfo
from src.device_information.network_info import NetworkInfo
from src.device_information.system_info import SystemInfo
from src.data_management import Writer
from src.builder import ComputerBuilder

file_name_gs = 'service_account.json'
google_sheet = 'hoja-tec'
sheet_name = 'db_tec'

if __name__ == '__main__':
    wr = Writer()
    data_device = ComputerBuilder(anydesk_provider=AnyDeskInfo(), hardware_provider=HardwareInfo(), system_provider=SystemInfo(), network_provider=NetworkInfo())
    new_data = data_device.get_all_data()
    wr.update_local_storage(new_data.to_dictionary())
    google = GoogleSheet(file_name_gs, google_sheet, sheet_name)
    
    # Se debe evaluar la conexión a internet para discernir si se envian los datos
    # mediante la API de google o si se crea un archivo script para su ejeccución
    # posterior de 1 sola ejecución.

    def generate_uid():
        # Genera un ID leyendo la cantidad de filas habidas en la hoja de google
        # a partir de la fila de encabezados A1.
        pass

    # uid = generate_uid()
    # values = dictionary

    # Se pasan el ID y los datos en formato de diccionario o lista de lista para
    # la escritura del nuevo equipo en la hoja.
    # google.upload_profile(uid, values)
    
