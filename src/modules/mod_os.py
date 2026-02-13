from src.command_processor import CommandProcessor

class OperativeSystem:

    def __init__(self):
        self.class_computersystem = "Win32_OperatingSystem"
        self.get_os_data = CommandProcessor(self.class_computersystem).get_parsed_output()

    # Gets the Windows product name.
    def win_product(self):
        return self.get_os_data.get("Caption")
    
    # Gets the architecture bits of the OS.
    def win_architecture(self):
        return self.get_os_data.get("OSArchitecture")
    
    def get_windows_version(self):
        concat_win_product = f"{self.win_product()} {self.win_architecture()}" 
        return concat_win_product