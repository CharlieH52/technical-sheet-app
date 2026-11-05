"""Lectura del ID de AnyDesk desde system.conf.

Ruta preferente: ``%PROGRAMDATA%\\AnyDesk\\system.conf`` (instalación para todos
los usuarios). Respaldo: ``%APPDATA%\\AnyDesk\\system.conf``. No se usa
``os.getlogin()`` ni rutas hardcodeadas con el nombre del usuario.
"""

from __future__ import annotations

import os
from src.infra.diagnostics import diagnostics


class AnyDeskInfo:
    def __init__(self):
        self.id_key = "ad.anynet.id"
        self.none_id = 0

        program_data = os.getenv("PROGRAMDATA", r"C:\ProgramData")
        app_data = os.getenv("APPDATA", "")
        candidates = [
            os.path.join(program_data, "AnyDesk", "system.conf"),
        ]
        if app_data:
            candidates.append(os.path.join(app_data, "AnyDesk", "system.conf"))

        self.config_candidates = candidates
        self.config_file = next(
            (path for path in candidates if os.path.isfile(path)), candidates[0]
        )
        diagnostics.record("anydesk_config", self.config_file, "environment")

    def _read_config_file(self, file_path: str) -> dict[str, str] | None:
        config: dict[str, str] = {}
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as file:
                for line in file:
                    key, sep, value = line.partition("=")
                    if not sep:
                        continue
                    config[key.strip()] = value.strip()
            return config
        except (FileNotFoundError, OSError):
            return None

    def get_anydesk_desktop_id(self) -> int:
        for path in self.config_candidates:
            config = self._read_config_file(path)
            if not config:
                continue
            raw_value = config.get(self.id_key)
            if raw_value is None:
                continue
            try:
                value = int(raw_value)
            except (TypeError, ValueError):
                continue
            diagnostics.record("anydesk_id", value, "file")
            return value

        diagnostics.warn("No se encontró ad.anynet.id en las rutas de AnyDesk.")
        diagnostics.record("anydesk_id", self.none_id, "none")
        return self.none_id