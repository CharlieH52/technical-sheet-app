"""Resolución de identidad del equipo (device_uuid + hardware_ids)."""

from __future__ import annotations

import re
import uuid

from src.infra import registry

_INVALID_UUIDS = {
    "00000000-0000-0000-0000-000000000000",
    "ffffffff-ffff-ffff-ffff-ffffffffffff",
}


def _clean(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).replace("\x00", " ").strip()
    text = re.sub(r"\s+", " ", text)
    if not text or text.lower() in {"", "default string", "to be filled by o.e.m.", "none"}:
        return None
    return text


def _valid_uuid(value: str | None) -> str | None:
    if not value:
        return None
    text = value.strip().lower()
    if text in _INVALID_UUIDS:
        return None
    try:
        parsed = uuid.UUID(text)
    except (ValueError, AttributeError):
        return None
    if parsed.version == 4 and parsed.variant != uuid.RFC_4122:
        pass
    canonical = str(parsed)
    if canonical in _INVALID_UUIDS:
        return None
    # Descartar UUIDs con todos los bytes iguales.
    if len(set(canonical.replace("-", ""))) == 1:
        return None
    return canonical.upper()


def _wmi_value(cls_name: str, property_name: str, namespace: str = "root\\cimv2") -> str | None:
    try:
        import win32com.client

        locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        svc = locator.ConnectServer(".", namespace)
        for item in svc.ExecQuery(f"SELECT {property_name} FROM {cls_name}"):
            value = getattr(item, property_name, None)
            cleaned = _clean(value)
            if cleaned:
                return cleaned
    except Exception:  # noqa: BLE001
        return None
    return None


def _first_physical_mac() -> str | None:
    try:
        import win32com.client

        locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        svc = locator.ConnectServer(".", "root\\cimv2")
        candidates = []
        for adapter in svc.ExecQuery(
            "SELECT Name, MACAddress, PhysicalAdapter, PNPDeviceID FROM Win32_NetworkAdapter"
        ):
            mac = _clean(getattr(adapter, "MACAddress", None))
            if not mac:
                continue
            if getattr(adapter, "PhysicalAdapter", None) is not True:
                continue
            name = _clean(getattr(adapter, "Name", None)) or ""
            pnp = _clean(getattr(adapter, "PNPDeviceID", None)) or ""
            score = 0
            if "pci" in pnp.lower():
                score += 5
            if "ethernet" in name.lower() or "wi-fi" in name.lower() or "wifi" in name.lower():
                score += 2
            candidates.append((score, mac, name))
        if candidates:
            candidates.sort(key=lambda item: (-item[0], item[2]))
            # Normalizar MAC a colones.
            mac = candidates[0][1]
            digits = "".join(ch for ch in mac if ch.isalnum())
            if len(digits) == 12:
                return ":".join(digits[i : i + 2] for i in range(0, 12, 2)).upper()
            return mac.upper()
    except Exception:  # noqa: BLE001
        return None
    return None


def resolve_identity() -> tuple[str | None, str, dict[str, str | None]]:
    """Resuelve ``device_uuid`` y ``hardware_ids``.

    Devuelve ``(device_uuid, identity_source, hardware_ids)``. Si no se puede
    obtener ningún identificador estable, ``device_uuid`` es ``None``.
    """
    system_uuid = _wmi_value("Win32_ComputerSystemProduct", "UUID")
    board_serial = _wmi_value("Win32_BaseBoard", "SerialNumber")
    bios_serial = _wmi_value("Win32_BIOS", "SerialNumber")
    chassis_serial = _wmi_value("Win32_SystemEnclosure", "SerialNumber")
    nic_mac = _first_physical_mac()
    machine_guid = None
    try:
        import winreg

        machine_guid = registry.read_value(
            winreg.HKEY_LOCAL_MACHINE,
            "SOFTWARE\\Microsoft\\Cryptography",
            "MachineGuid",
        )
    except Exception:  # noqa: BLE001
        machine_guid = None

    hardware_ids = {
        "system_uuid": _valid_uuid(system_uuid),
        "board_serial": board_serial,
        "bios_serial": bios_serial,
        "chassis_serial": chassis_serial,
        "nic_mac": nic_mac,
        "machine_guid": _clean(machine_guid),
    }

    valid_smbios = _valid_uuid(system_uuid)
    if valid_smbios:
        return valid_smbios, "smbios", hardware_ids

    if board_serial or bios_serial:
        seed = f"{board_serial or ''}\x1f{bios_serial or ''}"
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, seed)).upper(), "board", hardware_ids

    if nic_mac:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"nic:{nic_mac}")).upper(), "nic_mac", hardware_ids

    if machine_guid:
        cleaned = _clean(machine_guid)
        try:
            parsed = uuid.UUID(cleaned)  # type: ignore[arg-type]
            return str(parsed).upper(), "machine_guid", hardware_ids
        except (ValueError, AttributeError):
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"machine:{cleaned}")).upper(), "machine_guid", hardware_ids

    return None, "none", hardware_ids
