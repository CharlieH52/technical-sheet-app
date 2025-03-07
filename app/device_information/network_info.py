import psutil

class NetworkInfo:
    
    default_name_adapter = 'Ethernet'
    keys = ['MAC', 'IP4', 'IP6_1', 'IP6_2', 'IP6_temp', 'IP6_link']
    address_list = []

    def __init__(self):
        self.network_info = {}
        self._get_network_data()
        self.make_dictionary()
    
    # Obtiene la direccion IP del adaptador Ethernet principal.
    def _get_network_data(self):
        try:
            for interface, info in psutil.net_if_addrs().items():
                if interface == self.default_name_adapter:
                    for data in info:
                        self.address_list.append(data.address)
            
        except Exception as e:
            print(e)

    def make_dictionary(self):
        for key, value in zip(self.keys, self.address_list):
            self.network_info[key] = value