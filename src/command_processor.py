import subprocess

class CommandProcessor:
    def __init__(self, command: str):
        self.command = command
        
    def __execute_command(self) -> subprocess.CompletedProcess:
        pswCommand = ["powershell", "get-ciminstance", f"-class {self.command} | Select-Object * | Format-List"]
        output = subprocess.run(pswCommand, text=True, capture_output=True, shell=True)
        return output
    
    def get_parsed_output(self) -> dict[str, str]:
        output = self.__execute_command()
        command_data = {}
        for line in output.stdout.splitlines():
            key, sep, value = line.partition(":")
            if not sep:
                continue
            command_data[key.strip()] = value.strip()
        return command_data