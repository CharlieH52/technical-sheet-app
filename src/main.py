from modules.mod_anydesk import AnyDeskInfo
from modules.mod_hardware import HardwareInfo
from modules.mod_network import NetworkInfo
from modules.mod_os import OperativeSystem
from modules.mod_user import UserInformation 
from repository.computer_repository import ComputerRepositoryLocal
from computer_builder import ComputerBuilder
from notifications.popup import PopUp

# REMOTESAVE = True

if __name__ == "__main__":
    crl = ComputerRepositoryLocal()
    data_device = ComputerBuilder(anydesk_provider=AnyDeskInfo(), user_provider=UserInformation(), hardware_provider=HardwareInfo(), system_provider=OperativeSystem(), network_provider=NetworkInfo())
    computer = data_device.create_computer()
    computer_data = computer.to_dictionary()

    crl.find_and_update_by_mac(computer_data)

    PopUp("Estado", "Ficha guardada correctamente.")

    # if SHEET_FUNCTION == True:
    #     ApiClient(computer_data).post_computer_data(computer_data)