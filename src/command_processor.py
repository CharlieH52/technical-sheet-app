import subprocess
import json

class CommandProcessor:
    def __init__(self, command: list):
        self.command = command

    # IMPORTANT
    # You need to be sure that your command list returns text with the pipeline "FORMAT-LIST"

    def __execute_command(self) -> subprocess.CompletedProcess:
        pswCommand = self.command
        return subprocess.run(pswCommand, text=True, capture_output=True, shell=True)

    def get_output_dictionary(self) -> dict[str, str]:
        output = self.__execute_command()
        command_data = {}
        for line in output.stdout.splitlines():
            key, sep, value = line.partition(":")
            if not sep:
                continue
            command_data[key.strip()] = value.strip()
        return command_data
    
    def get_from_json(self) -> list[dict[str, str]]:
        output = self.__execute_command()
        return json.loads(output.stdout)
        