from app.modules.mod_anydesk import AnyDeskInfo
from app.modules.mod_hardware import HardwareInfo
from app.modules.mod_network import NetworkInfo
from app.modules.mod_os import OperativeSystem
from app.modules.mod_user import UserInformation 
from app.repository.computer_repository import ComputerRepositoryLocal
from app.computer_builder import ComputerBuilder

def main():
    crl = ComputerRepositoryLocal()
    data_device = ComputerBuilder(
        anydesk_provider=AnyDeskInfo(),
        user_provider=UserInformation(),
        hardware_provider=HardwareInfo(),
        system_provider=OperativeSystem(),
        network_provider=NetworkInfo()
        )
    computer = data_device.create_computer()
    computer_data = computer.to_dictionary()

    crl.find_and_update_by_mac(computer_data)

if __name__ == "__main__":
    main()