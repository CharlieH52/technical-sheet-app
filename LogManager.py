import time
import os
from platform import node

class LogManagerSystem:
    folder_name = 'LOGS'
    
    def __init__(self):
        self.machine_name = node()
        self.op_log_directory = self.output_route()
        
    def output_route(self):
        logs_directory = os.path.join(os.getcwd(), self.folder_name)
        return logs_directory

    def error_logs_print(self, directory, log):
        date = str(time.strftime('%d-%m-%Y_%H-%M-%S'))
        log_name = f'ERROR_LOG-{date}-{self.machine_name}.log'
        new_directory = os.path.join(directory, log_name)       
        with open(new_directory, 'w') as file:
            file.write(log)