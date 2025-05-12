from src.google_connect.google_actions import GoogleSheet
from src.device_information.anydesk_info import AnyDeskInfo
from src.device_information.hardware_info import HardwareInfo
from src.device_information.network_info import NetworkInfo
from src.device_information.system_info import SystemInfo
from src.data_management import Writer
from src.builder import ComputerBuilder

# Do you need use the API?
SHEET_FUNCTION = False

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
        google = GoogleSheet(file_name_gs, google_sheet, sheet_name)
    
