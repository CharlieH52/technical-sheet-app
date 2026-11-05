"""Pruebas de captura nativa: versión de Windows, diagnóstico y DIMM único."""

from __future__ import annotations

import os
import unittest

from src.infra.diagnostics import Diagnostics
from src.infra.hardware_registry import read_cpu_name, read_motherboard
from src.infra.windows_version import (
    format_windows_version,
    normalize_architecture,
    normalize_product_name,
    read_windows_version,
)
from src.modules.mod_hardware import HardwareInfo


class WindowsVersionTest(unittest.TestCase):
    def test_corrige_windows_10_a_11_por_build(self) -> None:
        self.assertEqual(
            normalize_product_name("Windows 10 Pro", 26300, "Professional"),
            "Windows 11 Pro",
        )

    def test_respeta_windows_10_real(self) -> None:
        self.assertEqual(
            normalize_product_name("Windows 10 Pro", 19045, "Professional"),
            "Windows 10 Pro",
        )

    def test_quita_prefijo_microsoft(self) -> None:
        self.assertEqual(
            normalize_product_name("Microsoft Windows 11 Pro", 22631, "Professional"),
            "Windows 11 Pro",
        )

    def test_infiere_producto_si_falta(self) -> None:
        self.assertEqual(
            normalize_product_name(None, 26300, "Professional"),
            "Windows 11 Pro",
        )

    def test_formato_con_display_version(self) -> None:
        self.assertEqual(
            format_windows_version("Windows 11 Pro", 26300, 9711, "26H2"),
            "Windows 11 Pro 26H2 (26300.9711)",
        )

    def test_formato_sin_display_version(self) -> None:
        self.assertEqual(
            format_windows_version("Windows 10 Pro", 19045, 3803, None),
            "Windows 10 Pro (19045.3803)",
        )

    def test_arquitectura(self) -> None:
        self.assertEqual(normalize_architecture("AMD64"), "x64")
        self.assertEqual(normalize_architecture("ARM64"), "ARM64")
        self.assertEqual(normalize_architecture("x86"), "x86")

    @unittest.skipUnless(os.name == "nt", "requiere registro de Windows")
    def test_lee_version_desde_registro(self) -> None:
        info = read_windows_version()
        self.assertTrue(info.product)
        self.assertIsNotNone(info.build)
        self.assertTrue(info.formatted)
        self.assertLessEqual(len(info.formatted), 100)

    @unittest.skipUnless(os.name == "nt", "requiere registro de Windows")
    def test_lee_cpu_y_placa(self) -> None:
        cpu, cpu_source = read_cpu_name()
        board = read_motherboard()
        self.assertTrue(cpu)
        self.assertIn(cpu_source, {"registry", "environment", "none"})
        self.assertIn(board.source, {"registry", "none"})


class DiagnosticsTest(unittest.TestCase):
    def test_recoge_fuentes_valores_y_avisos(self) -> None:
        diag = Diagnostics()
        diag.record("cpu_info", "AMD Ryzen", "registry", note="ok")
        diag.warn("WMI no disponible")
        diag.warn("WMI no disponible")  # no se duplica

        payload = diag.as_dict()
        self.assertEqual(payload["sources"]["cpu_info"], "registry")
        self.assertEqual(payload["values"]["cpu_info"], "AMD Ryzen")
        self.assertEqual(payload["notes"]["cpu_info"], "ok")
        self.assertEqual(payload["warnings"], ["WMI no disponible"])

    def test_clear(self) -> None:
        diag = Diagnostics()
        diag.record("x", 1, "test")
        diag.clear()
        self.assertEqual(diag.as_dict()["sources"], {})


class SingleDimmTest(unittest.TestCase):
    def test_un_solo_dimm_no_revienta(self) -> None:
        info = HardwareInfo.__new__(HardwareInfo)
        info.physicalmemory = {
            "Caption": "Memoria física",
            "Manufacturer": "A-DATA",
            "PartNumber": "AD5U480016G-S",
            "Model": None,
            "Tag": "Physical Memory 0",
            "BankLabel": "BANK 0",
            "Capacity": 17179869184,
            "Speed": 4800,
            "ConfiguredClockSpeed": 4800,
            "ConfiguredVoltage": 1100,
            "DeviceLocator": "DIMM 0",
        }

        dimms = info.create_ram_objects()
        self.assertEqual(len(dimms), 1)
        self.assertEqual(dimms[0].capacity, 16)
        self.assertEqual(dimms[0].speed, 4800)

    def test_campos_ausentes_no_revientan(self) -> None:
        info = HardwareInfo.__new__(HardwareInfo)
        info.physicalmemory = [{"Capacity": None, "Speed": None, "ConfiguredVoltage": None}]

        dimms = info.create_ram_objects()
        self.assertIsNone(dimms[0].capacity)
        self.assertIsNone(dimms[0].speed)


if __name__ == "__main__":
    unittest.main()
