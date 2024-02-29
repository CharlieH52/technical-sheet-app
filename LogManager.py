import time
import os
import platform

class LogManagerSystem:
    def __init__(self):
        self.folder_name = 'LOGS'
        self.machine_name = platform.node()
        self.op_log_directory = self.output_route()
        
    def output_route(self):
        logs_directory = os.path.join(os.getcwd(), self.folder_name)
        return logs_directory

    def error_logs_print(self, directory, log):
        date = str(time.strftime('%d-%m-%Y_%H-%M-%S'))
        log_name = f'ERROR_LOG-{self.machine_name}-{date}.log'
        new_directory = os.path.join(directory, log_name)       
        with open(new_directory, 'w') as file:
            file.write(log)