from app.modules.mod_anydesk import AnyDeskInfo
from app.modules.mod_hardware import HardwareInfo
from app.modules.mod_network import NetworkInfo
from app.modules.mod_os import OperativeSystem
from app.modules.mod_user import UserInformation 
from app.repository.computer_repository import ComputerRepositoryLocal
from app.computer_builder import ComputerBuilder

def main():
    crl = ComputerRepositoryLocal()
    current_computer_list = crl.create_computer_list()
    new_computer = ComputerBuilder(
        anydesk_provider=AnyDeskInfo(),
        user_provider=UserInformation(),
        hardware_provider=HardwareInfo(),
        system_provider=OperativeSystem(),
        network_provider=NetworkInfo()
        ).create_computer()
    updated_computer_list = crl.find_and_update_by_mac(current_computer_list, new_computer)
    crl.save_data_in_file(updated_computer_list)
if __name__ == "__main__":
    main()