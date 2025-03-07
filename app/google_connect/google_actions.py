import gspread
import pandas as pd
from app.device_information.device_information import DeviceInformation

a = DeviceInformation()

class GoogleSheet:
    def __init__(self, file_name, document, sheet_name):
        self.gc = gspread.service_account(filename = file_name)
        self.sh = self.gc.open(document)
        self.sheet = self.sh.worksheet(sheet_name)
    
    def get_values(self):
        for key, item in a.device_info.items():
            print(f'{key}: {item}')

    def upload_profile(self, uid, profile_dict=None):
        # print(pd.DataFrame(self.sheet.get_all_records()))
        pass