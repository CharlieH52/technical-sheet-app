from app.command_processor import CommandProcessor

class NetworkInfo:
    def __init__(self):
        self.command_netipconfig = ['powershell', 'get-netipconfiguration -detailed | where-object {$_.IPv4Address -ne $none -and $_.IPv4DefaultGateway -ne $none -and $_.DNSServer -ne $none} | format-list']
        self.network_data = CommandProcessor(self.command_netipconfig).get_output_dictionary()
    
    def get_ip_address(self):
        return self.network_data.get("IPv4Address")
    
    def get_mac_address(self):
        return self.network_data.get("NetAdapter.LinkLayerAddress")
    
    def get_gateway_address(self):
        return self.network_data.get("IPv4DefaultGateway")

    def get_dns_address(self):
        return self.network_data.get("DNSServer")

    def get_adapter_name(self):
        return self.network_data.get("InterfaceAlias")

    def get_net_privacy(self):
        return self.network_data.get("NetProfile.NetworkCategory")

    def get_net_status(self):
        return self.network_data.get("NetProfile.IPv4Connectivity")

    def get_driver_name(self):
        return self.network_data.get("InterfaceDescription")