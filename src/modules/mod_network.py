"""Información de red basada en ``psutil`` y el registro.

Sustituye las consultas PowerShell anteriores. Expone la API que consume
``ComputerBuilder`` (``get_ip_address``, ``get_mac_address``) y añade gateway,
DNS, nombre del adaptador y el snapshot completo de interfaces.
"""

from src.infra.diagnostics import diagnostics
from src.infra.netinfo import (
    NetworkSnapshot,
    collect_network_snapshot,
    normalize_mac,
)


class NetworkInfo:
    def __init__(self):
        self.snapshot: NetworkSnapshot = collect_network_snapshot()
        self.active = self.snapshot.active
        self.interfaces = self.snapshot.interfaces

        active_mac = self.active.mac if self.active else None
        active_ip = self.active.ipv4 if self.active else None
        adapter_name = self.active.name if self.active else None
        gateway = self.active.gateway if self.active else None
        dns_servers = self.active.dns_servers if self.active else ()

        diagnostics.record("machine_mac", active_mac, self.snapshot.source)
        diagnostics.record("machine_ip", active_ip, self.snapshot.source)
        diagnostics.record("network_adapter", adapter_name, self.snapshot.source)
        diagnostics.record("network_gateway", gateway, "registry")
        diagnostics.record(
            "network_dns",
            ", ".join(dns_servers) if dns_servers else None,
            "registry",
        )
        diagnostics.record("network_outbound_ip", self.snapshot.outbound_ip, "psutil")
        if not active_mac:
            diagnostics.warn("No se detectó ninguna interfaz física activa con MAC.")
        if self.snapshot.virtual_names:
            diagnostics.warn(
                "Adaptadores virtuales excluidos: "
                + ", ".join(self.snapshot.virtual_names)
            )

    # API consumida por ComputerBuilder
    def get_ip_address(self) -> str | None:
        return self.active.ipv4 if self.active else None

    def get_mac_address(self) -> str | None:
        return self.active.mac if self.active else None

    # Compatibilidad con la API anterior
    def get_gateway_address(self) -> str | None:
        return self.active.gateway if self.active else None

    def get_dns_address(self) -> str | None:
        active = self.active
        if not active or not active.dns_servers:
            return None
        return ", ".join(active.dns_servers)

    def get_adapter_name(self) -> str | None:
        return self.active.name if self.active else None

    def get_net_privacy(self) -> None:
        return None

    def get_net_status(self) -> None:
        return None

    def get_driver_name(self) -> str | None:
        return self.active.name if self.active else None

    def get_interface_list(self) -> list[dict[str, str | bool | None]]:
        """Lista serializable de interfaces (útil para diagnóstico/payload)."""
        return [
            {
                "name": item.name,
                "mac": item.mac,
                "ipv4": item.ipv4,
                "netmask": item.netmask,
                "gateway": item.gateway,
                "dns_servers": ", ".join(item.dns_servers),
                "is_up": item.is_up,
                "is_virtual": item.is_virtual,
            }
            for item in self.interfaces
        ]
