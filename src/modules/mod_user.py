import getpass

from src.command_processor import CommandProcessor

class UserInformation:
    GET_USER_NAME = f"wmic useraccount where name='{getpass.getuser()}' get /all /format:list"

    def __init__(self):
        self.useraccount = CommandProcessor(self.GET_USER_NAME).get_parsed_output()

    def get_all_data(self) -> dict:
        user_data = self.useraccount
        return user_data
    
    def get_domain_name(self) -> str:
        return self.useraccount['Domain']

    def get_user_name(self) -> str:
        return self.useraccount['Name']

    def get_full_name(self) -> str:
        parse_name = rf"{self.get_domain_name()}\{self.get_user_name()}"
        return parse_name 