import psutil


class NetworkInfo:
    DEFAULT_ADAPTER = 'Ethernet'
    KEYS = ['MAC', 'IP4', 'IP6_1', 'IP6_2', 'IP6_temp', 'IP6_link']
    
    def __init__(self, adapter_name: str = None):
        self.adapter = adapter_name or self.DEFAULT_ADAPTER
        self.address_list = []
        self.network_info = {}
    
    # Obtiene la direccion IP del adaptador Ethernet principal.
    def _get_network_data(self):
        try:
            interfaces = psutil.net_if_addrs()
            if self.adapter not in interfaces:
                raise ValueError(f'{self.adapter} not found.')
            
            for data in interfaces[self.adapter]:
                self.address_list.append(data.address)
            
        except Exception as e:
            print(e)
    
    def build_info_dict(self):
        self.network_info = dict(zip(self.KEYS, self.address_list))
        
    def get_info(self):
        self._get_network_data()
        self.build_info_dict()
        return self.network_info