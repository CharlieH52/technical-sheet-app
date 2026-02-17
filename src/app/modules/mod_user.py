from app.command_processor import CommandProcessor

class UserInformation:
    def __init__(self):
        self.command_netconfig = ['powershell', 'get-ciminstance -class Win32_NetworkLoginProfile | Select-Object * | Where-Object { $_.UserType -like "Normal Account" } | Format-List']
        self.useraccount = CommandProcessor(self.command_netconfig).get_output_dictionary()
    
    def get_domain_name(self):
        return self.useraccount.get("Name")

    def get_user_name(self):
        return self.useraccount.get("Caption")

    def get_full_name(self):
        return self.useraccount.get("FullName")