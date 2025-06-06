from src.command_processor import CommandProcessor

class OperativeSystem:
    GET_OS_DATA = "wmic os get caption, osarchitecture /format:list"

    def __init__(self):
        self.os_data = CommandProcessor(self.GET_OS_DATA).get_parsed_output()

    # Gets the Windows product name.
    def win_product(self):
        return self.os_data['Caption']
    
    # Gets the architecture bits of the OS.
    def win_architecture(self):
        return self.os_data['OSArchitecture']
    
    def get_windows_version(self):
        concat_win_product = f"{self.win_product()} {self.win_architecture()}" 
        return concat_win_product