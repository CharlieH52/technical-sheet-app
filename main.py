from src.modules.mod_anydesk import AnyDeskInfo
from src.modules.mod_hardware import HardwareInfo
from src.modules.mod_network import NetworkInfo
from src.modules.mod_os import OperativeSystem
from src.modules.mod_user import UserInformation 
from src.data_management import Writer
from src.builder import ComputerBuilder
# from src.connector import ApiClient
from src.notifications.popup import PopUp

# Do you need use the API?
# SHEET_FUNCTION = True

if __name__ == "__main__":
    wr = Writer()
    data_device = ComputerBuilder(anydesk_provider=AnyDeskInfo(), user_provider=UserInformation(), hardware_provider=HardwareInfo(), system_provider=OperativeSystem(), network_provider=NetworkInfo())
    computer = data_device.create_computer()
    computer_data = computer.to_dictionary()

    wr.find_and_update_by_mac(computer_data)

    PopUp("Estado", "Ficha guardada correctamente.")

    # if SHEET_FUNCTION == True:
    #     ApiClient(computer_data).post_computer_data(computer_data)