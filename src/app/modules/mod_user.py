from src.app.command_processor import CommandProcessor

class UserInformation:
    def __init__(self):
        self.command_netconfig = ['powershell', 'get-ciminstance -class Win32_UserAccount | Select-Object * | Where-Object { $_.Status -like "Ok" } | Format-List']
        self.useraccount = CommandProcessor(self.command_netconfig).get_output_dictionary()
    
    def get_domain_name(self):
        return self.useraccount.get("Domain")

    def get_user_name(self):
        return self.useraccount.get("Name")

    def get_full_name(self):
        return self.useraccount.get("Caption")