"""Información del usuario de la sesión basada en ``getpass`` y el registro."""

from src.infra.diagnostics import diagnostics
from src.infra.userinfo import read_user_identity


class UserInformation:
    def __init__(self):
        self.identity = read_user_identity()
        diagnostics.record("user_name", self.identity.qualified, self.identity.source)

    def get_domain_name(self) -> str | None:
        """Nombre calificado ``DOMINIO\\usuario`` (consume ComputerBuilder)."""
        return self.identity.qualified

    def get_user_name(self) -> str | None:
        return self.identity.username

    def get_full_name(self) -> str | None:
        return self.identity.full_name
