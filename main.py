from src.google_connect.google_actions import GoogleSheet
from src.DataManagerClass import DataManager

file_name_gs = 'service_account.json'
google_sheet = 'hoja-tec'
sheet_name = 'db_tec'

google = GoogleSheet(file_name_gs, google_sheet, sheet_name)

if __name__ == '__main__':
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
    
    dm = DataManager()
    for i in dm.computer:
        print(i)
