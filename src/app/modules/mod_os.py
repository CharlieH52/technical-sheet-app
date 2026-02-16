from app.command_processor import CommandProcessor

class OperativeSystem:

    def __init__(self):
        self.class_computersystem = ["powershell", "get-ciminstance", "-class Win32_OperatingSystem | Select-Object * | Format-List"]
        self.get_os_data = CommandProcessor(self.class_computersystem).get_output_dictionary()

    # Gets the Windows product name.
    def win_product(self):
        return self.get_os_data.get("Caption")
    
    # Gets the architecture bits of your Windows.
    def win_architecture(self):
        return self.get_os_data.get("OSArchitecture")
    
    # Gets a large string with the Windows product and the architecture.
    def get_windows_version(self):
        concat_win_product = f"{self.win_product()} {self.win_architecture()}" 
        return concat_win_product