"""Diagnóstico de fuentes por campo.

Los proveedores anotan de dónde salió cada dato y con qué incidencias. Sirve
para ``--diagnose`` y, más adelante, para enviar ``diagnostics`` en el payload
de la API y detectar equipos con WMI roto en campo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FieldDiagnostic:
    field: str
    value: Any
    source: str | None
    note: str | None = None


@dataclass
class Diagnostics:
    _fields: dict[str, FieldDiagnostic] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def record(
        self,
        field_name: str,
        value: Any,
        source: str | None,
        note: str | None = None,
    ) -> None:
        self._fields[field_name] = FieldDiagnostic(
            field=field_name,
            value=value,
            source=source,
            note=note,
        )

    def warn(self, message: str) -> None:
        if message not in self.warnings:
            self.warnings.append(message)

    def get(self, field_name: str) -> FieldDiagnostic | None:
        return self._fields.get(field_name)

    def clear(self) -> None:
        self._fields.clear()
        self.warnings.clear()

    def as_dict(self) -> dict[str, Any]:
        return {
            "sources": {name: item.source for name, item in self._fields.items()},
            "values": {name: item.value for name, item in self._fields.items()},
            "notes": {
                name: item.note
                for name, item in self._fields.items()
                if item.note
            },
            "warnings": list(self.warnings),
        }


# Instancia compartida por los proveedores durante una ejecución.
diagnostics = Diagnostics()
