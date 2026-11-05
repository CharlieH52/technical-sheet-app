"""Pruebas de la etapa 2: red, usuario, unidades y migración de MAC."""

from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.infra.netinfo import (
    NetworkInterface,
    is_virtual_adapter,
    normalize_mac,
    select_active_interface,
)
from src.infra.units import bytes_to_gib
from src.infra.userinfo import read_user_identity


class NormalizeMacTest(unittest.TestCase):
    def test_guiones(self) -> None:
        self.assertEqual(normalize_mac("30-c5-99-d0-41-10"), "30:C5:99:D0:41:10")

    def test_dos_puntos(self) -> None:
        self.assertEqual(normalize_mac("30:C5:99:D0:41:10"), "30:C5:99:D0:41:10")

    def test_sin_separadores(self) -> None:
        self.assertEqual(normalize_mac("30C599D04110"), "30:C5:99:D0:41:10")

    def test_mayusculas(self) -> None:
        self.assertEqual(normalize_mac("08-bf-b8-84-67-4e"), "08:BF:B8:84:67:4E")

    def test_invalido(self) -> None:
        self.assertIsNone(normalize_mac("no-mac"))
        self.assertIsNone(normalize_mac("12"))
        self.assertIsNone(normalize_mac(None))


class VirtualAdapterTest(unittest.TestCase):
    def test_excluye(self) -> None:
        for name in (
            "vEthernet (WSL)",
            "Tailscale",
            "Loopback Pseudo-Interface 1",
            "Conexión de área local* 2",
        ):
            self.assertTrue(is_virtual_adapter(name), name)

    def test_fisico(self) -> None:
        self.assertFalse(is_virtual_adapter("Ethernet"))
        self.assertFalse(is_virtual_adapter("Wi-Fi"))


class ActiveSelectionTest(unittest.TestCase):
    def _iface(self, name, ip, gateway, mac, virtual=False, up=True):
        return NetworkInterface(
            name=name,
            mac=mac,
            ipv4=ip,
            netmask="255.255.255.0",
            gateway=gateway,
            dns_servers=(),
            is_up=up,
            is_virtual=virtual,
        )

    def test_prioriza_ip_saliente(self) -> None:
        eth = self._iface("Ethernet", "192.168.0.9", "192.168.0.1", "AA:BB:CC:DD:EE:FF")
        wifi = self._iface("Wi-Fi", "10.0.0.5", "10.0.0.1", "11:22:33:44:55:66")
        active = select_active_interface([eth, wifi], "10.0.0.5")
        self.assertEqual(active.name, "Wi-Fi")

    def test_prioriza_gateway_si_no_hay_saliente(self) -> None:
        eth = self._iface("Ethernet", "192.168.0.9", "192.168.0.1", "AA:BB:CC:DD:EE:FF")
        tailscale = self._iface(
            "Tailscale", "100.104.82.108", None, "BB:CC:DD:EE:FF:00", virtual=True
        )
        active = select_active_interface([eth, tailscale], None)
        self.assertEqual(active.name, "Ethernet")

    def test_excluye_virtuales(self) -> None:
        vswitch = self._iface(
            "vEthernet (WSL)", "172.26.112.1", None, "00:15:5D:8A:A3:F0", virtual=True
        )
        loopback = self._iface("Loopback", "127.0.0.1", None, None, virtual=True)
        active = select_active_interface([vswitch, loopback], None)
        self.assertIsNone(active)

    def test_fallback_mac_sin_ip(self) -> None:
        iface = self._iface("Ethernet", None, None, "AA:BB:CC:DD:EE:FF", up=True)
        active = select_active_interface([iface], None)
        self.assertEqual(active.mac, "AA:BB:CC:DD:EE:FF")


class UnitsTest(unittest.TestCase):
    def test_bytes_to_gib(self) -> None:
        self.assertEqual(bytes_to_gib(17179869184), 16)
        self.assertIsNone(bytes_to_gib(None))


class UserIdentityTest(unittest.TestCase):
    def test_calificado_con_dominio(self) -> None:
        with patch.dict(os.environ, {"USERNAME": "SISTEMAS2", "USERDOMAIN": "SISTEMAS"}, clear=False):
            with patch("src.infra.userinfo.getpass.getuser", return_value="SISTEMAS2"):
                identity = read_user_identity()
                self.assertEqual(identity.qualified, "SISTEMAS\\SISTEMAS2")
                self.assertEqual(identity.username, "SISTEMAS2")
                self.assertEqual(identity.domain, "SISTEMAS")

    def test_sin_dominio(self) -> None:
        with patch.dict(os.environ, {"USERNAME": "localuser", "USERDOMAIN": "LOCALUSER"}, clear=False):
            with patch("src.infra.userinfo.getpass.getuser", return_value="localuser"):
                identity = read_user_identity()
                self.assertEqual(identity.qualified, "localuser")


class MacMigrationTest(unittest.TestCase):
    def test_migra_guiones_a_dos_puntos(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "localStorage.db"
            conn = sqlite3.connect(db)
            conn.execute(
                "CREATE TABLE computers (machine_mac TEXT PRIMARY KEY, device_name TEXT, "
                "user_name TEXT, machine_ip TEXT, mobo_mark TEXT, mobo_model TEXT, "
                "cpu_info TEXT, operative_system TEXT, storage_model TEXT, "
                "storage_cap INTEGER, anydesk_id INTEGER)"
            )
            conn.execute(
                "CREATE TABLE dimm_ram (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "machine_mac TEXT NOT NULL, caption TEXT)"
            )
            conn.execute(
                "INSERT INTO computers VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                ("08-BF-B8-84-67-4E", "PC", "u", None, None, None, None, None, None, None, None),
            )
            conn.execute("INSERT INTO dimm_ram (machine_mac, caption) VALUES (?,?)", ("08-BF-B8-84-67-4E", "RAM"))
            conn.commit()
            conn.close()

            from src.repository.computer_repository_sqlite import ComputerRepositorySQLite

            ComputerRepositorySQLite(db)

            conn = sqlite3.connect(db)
            macs = [r[0] for r in conn.execute("SELECT machine_mac FROM computers").fetchall()]
            dimm_macs = [r[0] for r in conn.execute("SELECT machine_mac FROM dimm_ram").fetchall()]
            conn.close()

            self.assertEqual(macs, ["08:BF:B8:84:67:4E"])
            self.assertEqual(dimm_macs, ["08:BF:B8:84:67:4E"])


if __name__ == "__main__":
    unittest.main()
