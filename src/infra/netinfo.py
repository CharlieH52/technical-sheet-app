"""Inventario de interfaces de red con ``psutil`` y el registro de Windows.

Objetivo de la etapa: dejar de parsear ``Get-NetIPConfiguration`` y elegir
**una** interfaz física activa aunque convivan WSL, Hyper-V, Tailscale o
adaptadores Bluetooth. La MAC se normaliza a ``AA:BB:CC:DD:EE:FF`` (formato del
contrato de la API) y el gateway/DNS se leen del registro, porque ``psutil`` no
los expone en Windows.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
import re
import socket

import psutil

from src.infra import registry

try:  # pragma: no cover - solo Windows
    import winreg

    _HKLM = winreg.HKEY_LOCAL_MACHINE
except ImportError:  # pragma: no cover
    _HKLM = 0

_TCPIP_INTERFACES = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
_NETWORK_CLASS_TEMPLATE = (
    r"SYSTEM\CurrentControlSet\Control\Network"
    r"\{4d36e972-e325-11ce-bfc1-08002be10318}\{guid}\Connection"
)

# Coincidencias (en minúsculas) de adaptadores que no representan la red física
# del equipo. Se revisan contra el nombre que muestra Windows y contra el nombre
# del registro.
_VIRTUAL_MARKERS = (
    "vethernet",
    "hyper-v",
    "tailscale",
    "vmware",
    "loopback",
    "bluetooth",
    "virtualbox",
    "wsl",
    "teredo",
    "isatap",
    "6to4",
    "ip-https",
    "tap-windows",
    "openvpn",
    "zerotier",
    "wireguard",
    "docker",
    "npcap",
    "kernel debug",
    "depurador de kernel",
    "conexión de área local*",
    "conexion de area local*",
)

_LOOPBACK_PREFIXES = ("127.", "0.0.0.0", "169.254.")
_PUBLIC_PROBES = ("8.8.8.8", "1.1.1.1")


def normalize_mac(value: object) -> str | None:
    """Normaliza una MAC a ``AA:BB:CC:DD:EE:FF``.

    Acepta separadores ``-``, ``:``, espacios o la cadena hexadecimal sin
    separadores. Devuelve ``None`` si no contiene exactamente 12 dígitos
    hexadecimales, para no guardar valores basura como clave.
    """
    if value is None:
        return None
    digits = re.sub(r"[^0-9A-Fa-f]", "", str(value))
    if len(digits) != 12:
        return None
    upper = digits.upper()
    return ":".join(upper[index : index + 2] for index in range(0, 12, 2))


def is_virtual_adapter(name: str | None) -> bool:
    """Indica si el nombre corresponde a un adaptador virtual o no físico."""
    text = (name or "").strip().lower()
    return any(marker in text for marker in _VIRTUAL_MARKERS)


def _first_ipv4(addresses: list[psutil._common.snicaddr]) -> tuple[str | None, str | None]:
    """Devuelve la IPv4 y máscara preferidas de una interfaz."""
    fallback: tuple[str | None, str | None] = (None, None)
    for address in addresses:
        if address.family != 2:  # AF_INET
            continue
        ip = (address.address or "").strip()
        if not ip:
            continue
        if ip.startswith(_LOOPBACK_PREFIXES):
            if fallback[0] is None:
                fallback = (ip, address.netmask)
            continue
        return ip, address.netmask
    return fallback


def _first_mac(addresses: list[psutil._common.snicaddr]) -> str | None:
    """Extrae y normaliza la primera MAC de la interfaz."""
    for address in addresses:
        if address.family == getattr(psutil, "AF_LINK", -1):
            mac = normalize_mac(address.address)
            if mac:
                return mac
    return None


def _as_text_list(value: object) -> list[str]:
    """Convierte un valor REG_MULTI_SZ/REG_SZ en una lista sin vacíos."""
    return [item for item in registry.as_list(value) if item and item != "0.0.0.0"]


@dataclass(frozen=True)
class NetworkInterface:
    """Datos de una interfaz tal como los ve el equipo."""

    name: str
    mac: str | None
    ipv4: str | None
    netmask: str | None
    gateway: str | None
    dns_servers: tuple[str, ...]
    is_up: bool
    is_virtual: bool

    @property
    def is_physical(self) -> bool:
        return not self.is_virtual


@dataclass(frozen=True)
class NetworkSnapshot:
    """Resultado completo: todas las interfaces y la elegida como activa."""

    interfaces: tuple[NetworkInterface, ...]
    active: NetworkInterface | None
    outbound_ip: str | None
    source: str

    @property
    def virtual_names(self) -> tuple[str, ...]:
        return tuple(item.name for item in self.interfaces if item.is_virtual)


def detect_outbound_ipv4(timeout: float = 0.15) -> str | None:
    """Obtiene la IPv4 de salida sin enviar tráfico (UDP ``connect``).

    Si no hay ruta a Internet devuelve ``None``; el registro y el gateway
    siguen permitiendo elegir una interfaz.
    """
    for probe in _PUBLIC_PROBES:
        sock = None
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            sock.connect((probe, 80))
            address = sock.getsockname()[0]
            if address and not address.startswith(_LOOPBACK_PREFIXES):
                return address
        except OSError:
            continue
        finally:
            if sock is not None:
                sock.close()
    return None


def _interface_name(guid: str) -> str | None:
    """Nombre amigable (``Ethernet``) asociado al GUID de la interfaz."""
    path = _NETWORK_CLASS_TEMPLATE.replace("{guid}", guid)
    value = registry.read_value(_HKLM, path, "Name")
    text = str(value).strip() if value is not None else ""
    return text or None


@dataclass(frozen=True)
class _RegistryConfig:
    name: str | None
    ipv4: tuple[str, ...]
    gateway: str | None
    dns_servers: tuple[str, ...]


def _read_registry_configs() -> dict[str, _RegistryConfig]:
    """Lee IP, gateway y DNS de ``Tcpip\\Parameters\\Interfaces`` por GUID."""
    configs: dict[str, _RegistryConfig] = {}
    for guid in registry.list_subkeys(_HKLM, _TCPIP_INTERFACES):
        base = f"{_TCPIP_INTERFACES}\\{guid}"
        static_ips = _as_text_list(registry.read_value(_HKLM, base, "IPAddress"))
        dhcp_ip = _as_text_list(registry.read_value(_HKLM, base, "DhcpIPAddress"))
        ips = tuple(dict.fromkeys([*dhcp_ip, *static_ips]))

        dhcp_gateway = _as_text_list(
            registry.read_value(_HKLM, base, "DhcpDefaultGateway")
        )
        static_gateway = _as_text_list(
            registry.read_value(_HKLM, base, "DefaultGateway")
        )
        gateway = (dhcp_gateway or static_gateway or [None])[0]

        dns = _as_text_list(registry.read_value(_HKLM, base, "DhcpNameServer"))
        if not dns:
            dns = _as_text_list(registry.read_value(_HKLM, base, "NameServer"))
        # NameServer puede venir como "1.1.1.1,8.8.8.8" o "1.1.1.1 8.8.8.8".
        dns_servers = tuple(
            dict.fromkeys(
                item
                for raw in dns
                for item in re.split(r"[,;\s]+", raw)
                if item
            )
        )

        configs[guid] = _RegistryConfig(
            name=_interface_name(guid),
            ipv4=ips,
            gateway=gateway,
            dns_servers=dns_servers,
        )
    return configs


def _config_by_ip(
    configs: dict[str, _RegistryConfig]
) -> dict[str, _RegistryConfig]:
    by_ip: dict[str, _RegistryConfig] = {}
    for config in configs.values():
        for ip in config.ipv4:
            by_ip.setdefault(ip, config)
    return by_ip


def _config_by_name(
    configs: dict[str, _RegistryConfig]
) -> dict[str, _RegistryConfig]:
    by_name: dict[str, _RegistryConfig] = {}
    for config in configs.values():
        if config.name:
            by_name.setdefault(config.name.lower(), config)
    return by_name


def list_interfaces() -> tuple[NetworkInterface, ...]:
    """Enumera las interfaces visibles con ``psutil`` y las enriquece."""
    configs = _read_registry_configs()
    by_ip = _config_by_ip(configs)
    by_name = _config_by_name(configs)
    stats = psutil.net_if_stats()
    result: list[NetworkInterface] = []

    for name, addresses in psutil.net_if_addrs().items():
        ipv4, netmask = _first_ipv4(addresses)
        mac = _first_mac(addresses)
        if not ipv4 and not mac:
            continue

        config = by_ip.get(ipv4 or "") or by_name.get(name.lower())
        stat = stats.get(name)
        result.append(
            NetworkInterface(
                name=name,
                mac=mac,
                ipv4=ipv4,
                netmask=netmask,
                gateway=config.gateway if config else None,
                dns_servers=config.dns_servers if config else (),
                is_up=bool(getattr(stat, "isup", True)),
                is_virtual=is_virtual_adapter(name)
                or is_virtual_adapter(config.name if config else None),
            )
        )

    return tuple(result)


def _score(interface: NetworkInterface, outbound_ip: str | None) -> int:
    """Puntúa una interfaz para elegir la más representativa del equipo."""
    score = 0
    if outbound_ip and interface.ipv4 == outbound_ip:
        score += 100
    if interface.gateway:
        score += 20
    if interface.is_physical:
        score += 5
    name = interface.name.lower()
    if "ethernet" in name:
        score += 2
    if "wi-fi" in name or "wifi" in name or "wireless" in name:
        score += 1
    return score


def select_active_interface(
    interfaces: tuple[NetworkInterface, ...] | list[NetworkInterface],
    outbound_ip: str | None = None,
) -> NetworkInterface | None:
    """Elige la interfaz física activa.

    Prioridad: la que tiene la IP de salida, luego la que tiene gateway, luego
    cualquier física con IPv4 y finalmente cualquier física con MAC (aunque no
    tenga IP, para no perder la identidad por MAC).
    """
    physical = [item for item in interfaces if item.is_physical and item.is_up]
    with_ip = [item for item in physical if item.ipv4]
    if with_ip:
        return max(with_ip, key=lambda item: (_score(item, outbound_ip), item.name))

    with_mac = [item for item in physical if item.mac]
    if with_mac:
        return max(with_mac, key=lambda item: (_score(item, outbound_ip), item.name))
    return None


def collect_network_snapshot() -> NetworkSnapshot:
    """Reúne interfaces, IP de salida y la activa en una sola lectura."""
    interfaces = list_interfaces()
    outbound_ip = detect_outbound_ipv4()
    active = select_active_interface(interfaces, outbound_ip)
    source = "psutil+registry" if interfaces else "none"
    return NetworkSnapshot(
        interfaces=interfaces,
        active=active,
        outbound_ip=outbound_ip,
        source=source,
    )
