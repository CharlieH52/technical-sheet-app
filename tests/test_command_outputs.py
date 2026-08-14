from models.computer import Computer
from models.ram import DimmRam
from modules.mod_hardware import HardwareInfo
from computer_builder import ComputerBuilder
import json

computer_data = {
        "anydesk_id": 1787004049,
        "device_name": "DESKTOP-BOD5H58",
        "user_name": "DESKTOP-BOD5H58\\charlie",
        "machine_mac": "08-BF-B8-84-67-4E",
        "machine_ip": "192.168.0.66",
        "mobo_mark": "ASUSTeK COMPUTER INC.",
        "mobo_model": "PRIME H510M-K R2.0",
        "cpu_info": "Intel(R) Core(TM) i5-10400 CPU @ 2.90GHz",
        "operative_system": "Microsoft Windows 11 Pro 64 bits",
        "storage_model": "KINGSTON SA400S37480G",
        "storage_cap": 447,
        "dimm_list": []
        }

ram_data = '''{
            "Caption": "Memoria f\u00a1sica",
            "Manufacturer": "Corsair",
            "PartNumber": "CMK32GX4M2E3200C16  ",
            "Model": null,
            "Tag": "Physical Memory 0",
            "BankLabel": "BANK 0",
            "Capacity": 16,
            "Speed": 2666,
            "ConfiguredClockSpeed": 2666,
            "ConfiguredVoltage": 1200,
            "DeviceLocator": "ChannelA-DIMM1"
        }'''

# hinf = HardwareInfo()
# hinf.create_ram_objects()

def prueba_conceptual() -> list[dict[str,str]]:
    variable = json.loads(ram_data)
    return variable

datos = prueba_conceptual()
if type(datos) == dict:
    provicional = []
    provicional.append(datos)
    print(type(provicional))
    print(len(provicional))
    print(provicional)
else:
    print(type(datos))
    print(len(datos))
