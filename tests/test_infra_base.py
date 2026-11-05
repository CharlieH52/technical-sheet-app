"""Pruebas de la etapa base: rutas portátiles, logging e instancia única."""

from __future__ import annotations

import os
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from src.infra import paths
from src.infra.logging import (
    clear_log_files,
    configure_logging,
    current_log_path,
    get_logger,
    reset_logging,
)
from src.infra.single_instance import SingleInstance


class PathsTest(unittest.TestCase):
    def test_sqlite_path_es_portatil_por_defecto(self) -> None:
        with patch.dict(
            os.environ,
            {"APP_DIR": "", "SQLITE_PATH": "", "LOG_DIR": ""},
            clear=False,
        ):
            self.assertEqual(paths.sqlite_path().name, "localStorage.db")
            self.assertEqual(paths.sqlite_path().parent, paths.default_app_dir() / "data")
            self.assertEqual(paths.log_dir(), paths.default_app_dir() / "logs")

    def test_ensure_writable_dir_crea_y_escribe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "data" / "nested"
            result = paths.ensure_writable_dir(target)
            self.assertEqual(result, target)
            self.assertTrue(target.is_dir())

    def test_ensure_writable_dir_falla_si_el_padre_es_un_archivo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            blocker = Path(tmp) / "archivo.txt"
            blocker.write_text("x", encoding="utf-8")
            with self.assertRaises(paths.PortablePathError):
                paths.ensure_writable_dir(blocker / "sub")

    def test_migra_bd_legacy_a_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            legacy = Path(tmp) / "localStorage.db"
            legacy.write_bytes(b"contenido")

            with patch.dict(
                os.environ,
                {"APP_DIR": tmp, "SQLITE_PATH": ""},
                clear=False,
            ):
                migrated = paths.migrate_legacy_sqlite()
                self.assertIsNotNone(migrated)
                self.assertEqual(
                    migrated.resolve(),
                    (Path(tmp) / "data" / "localStorage.db").resolve(),
                )
                self.assertEqual(migrated.read_bytes(), b"contenido")
                self.assertTrue(legacy.exists())  # se conserva como respaldo

                self.assertIsNone(paths.migrate_legacy_sqlite())


class SingleInstanceTest(unittest.TestCase):
    def test_segunda_instancia_no_adquiere_el_mutex(self) -> None:
        name = rf"Local\TechnicalSheet.Test.{uuid.uuid4()}"
        first = SingleInstance(name)
        second = SingleInstance(name)
        third = SingleInstance(name)

        self.assertTrue(first.acquire())
        try:
            self.assertFalse(second.acquire())
        finally:
            first.release()

        self.assertTrue(third.acquire())
        third.release()


class LoggingTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.addCleanup(reset_logging)
        reset_logging()

    def test_escribe_en_log_dir_configurado(self) -> None:
        with patch.dict(
            os.environ,
            {"LOG_DIR": self._tmp.name, "PORTABLE_STRICT": "false"},
            clear=False,
        ):
            log_file = configure_logging(quiet=True)
            get_logger("test").info("mensaje de prueba")

            self.assertTrue(log_file.exists())
            self.assertIn("mensaje de prueba", log_file.read_text(encoding="utf-8"))
            self.assertEqual(current_log_path(), log_file)

            clear_log_files()
            self.assertFalse(log_file.exists())

    def test_fallback_a_temp_si_log_dir_no_es_escribible(self) -> None:
        blocker = Path(self._tmp.name) / "no-es-carpeta"
        blocker.write_text("x", encoding="utf-8")

        with patch.dict(
            os.environ,
            {"LOG_DIR": str(blocker), "PORTABLE_STRICT": "false"},
            clear=False,
        ):
            log_file = configure_logging(quiet=True)
            self.assertIn("TechnicalSheet", str(log_file))
            self.assertTrue(log_file.exists())

            # Cerrar handlers antes de borrar (Windows bloquea archivos abiertos).
            self.addCleanup(lambda: log_file.unlink(missing_ok=True))
            self.addCleanup(reset_logging)


if __name__ == "__main__":
    unittest.main()
