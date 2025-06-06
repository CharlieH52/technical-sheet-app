from src.modules.anydesk import AnyDeskInfo
from src.modules.hardware_info import HardwareInfo
from src.modules.network_info import NetworkInfo
from src.modules.system_info import SystemInfo
from src.data_management import Writer
from src.builder import ComputerBuilder
import requests

# Do you need use the API?
SHEET_FUNCTION = True

# Google Sheet Config Lines
file_name_gs = "service_account.json"
google_sheet = "hoja-tec"
sheet_name = "db_tec"

if __name__ == "__main__":
    wr = Writer()
    data_device = ComputerBuilder(anydesk_provider=AnyDeskInfo(), hardware_provider=HardwareInfo(), system_provider=SystemInfo(), network_provider=NetworkInfo())
    new_data = data_device.get_all_data()
    
    wr.find_and_update_by_mac(new_data.to_dictionary())

    if SHEET_FUNCTION == True:
        endpoint = "http://127.0.0.1:8000/post"
        inc_data = new_data.to_dictionary()
        response = requests.post(url=endpoint, json=inc_data)

    
