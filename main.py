from modules.mod_anydesk import AnyDeskInfo
from modules.mod_hardware import HardwareInfo
from modules.mod_network import NetworkInfo
from modules.mod_os import OperativeSystem
from modules.mod_user import UserInformation 
from src.data_management import Writer
from src.builder import ComputerBuilder
import requests

# Do you need use the API?
SHEET_FUNCTION = False

if __name__ == "__main__":
    wr = Writer()
    data_device = ComputerBuilder(anydesk_provider=AnyDeskInfo(), user_provider=UserInformation(), hardware_provider=HardwareInfo(), system_provider=OperativeSystem(), network_provider=NetworkInfo())
    new_data = data_device.get_all_data()
    
    wr.find_and_update_by_mac(new_data.to_dictionary())

    if SHEET_FUNCTION == True:
        endpoint = "http://127.0.0.1:8000/post"
        inc_data = new_data.to_dictionary()
        response = requests.post(url=endpoint, json=inc_data)
