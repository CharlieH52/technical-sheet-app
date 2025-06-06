import subprocess

class CommandProcessor:
    def __init__(self, command: str):
        self.command = command
        
    def __execute_command(self):
        output = subprocess.getoutput(self.command)
        return output
    
    def __clean_list(self, data_list: list) -> list:
        cleaned_list = []
        for item in data_list:
            if not '' == item:
                cleaned_list.append(item)
        return cleaned_list
    
    def __to_dict(self, cleaned_list: list) -> dict[str,str]:
        parsed_dict = {}
        for item in cleaned_list:
            key, data = item.split('=', 1)
            parsed_dict[key] = data
        return parsed_dict

    def get_parsed_output(self) -> dict[str,str]:
        to_parse = self.__execute_command().split('\n')
        cleaned_list = self.__clean_list(to_parse)
        obj_dict = self.__to_dict(cleaned_list=cleaned_list)
        return obj_dict