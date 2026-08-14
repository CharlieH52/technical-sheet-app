"""
================================================================================
  popup.py – Sistema de notificaciones y logging de errores
================================================================================

  Clases disponibles:
    • ErrorLogger   – Escribe mensajes de error en un archivo .log local.
    • PopUp         – Muestra un messagebox de información.
    • PopUpWarning  – Muestra un messagebox de advertencia.
    • PopUpError    – Muestra un messagebox de error crítico.

  Comportamiento especial de PopUp / PopUpWarning / PopUpError:
  ──────────────────────────────────────────────────────────────
  Si el content_message supera los 64 caracteres, el texto completo se
  guarda automáticamente en un archivo .log en el directorio de trabajo
  (error_logs.txt) y al usuario se le presenta un resumen junto con la
  ruta del archivo generado.

================================================================================
"""

import os
import datetime
from tkinter import messagebox, Tk


class ErrorLogger:
    """
    Gestor de archivos de log para mensajes de error extensos.

    Escribe entradas con marca de tiempo en un archivo de texto plano
    ubicado en el directorio de trabajo actual.
    """

    LOG_FILE_NAME: str = "error_logs.txt"

    @classmethod
    def _get_log_path(cls) -> str:
        """Retorna la ruta absoluta al archivo de log."""
        return os.path.join(os.getcwd(), cls.LOG_FILE_NAME)

    @classmethod
    def log(cls, title: str, message: str) -> str:
        """
        Escribe una entrada de error en el archivo de log.

        Args:
            title: Título o categoría del error.
            message: Mensaje completo del error.

        Returns:
            Ruta absoluta del archivo de log donde se escribió la entrada.
        """
        log_path = cls._get_log_path()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        separator = "=" * 60

        entry = (
            f"[{timestamp}]  TÍTULO: {title}"
            f"[{timestamp}]  MENSAJE: {message}"
            f"{separator}"
        )

        with open(log_path, "a", encoding="utf-8") as file:
            file.write(entry)

        return log_path

    @classmethod
    def clear_logs(cls) -> None:
        """Elimina el archivo de log si existe."""
        log_path = cls._get_log_path()
        if os.path.exists(log_path):
            os.remove(log_path)


class _BasePopUp:
    """
    Clase base abstracta para todos los tipos de PopUp.

    Si el mensaje excede MAX_MESSAGE_LENGTH caracteres, se delega el texto
    completo a ErrorLogger y al usuario se muestra un resumen.
    """

    MAX_MESSAGE_LENGTH: int = 64

    def __init__(self, window_title: str, content_message: str):
        self.window_title = window_title
        self.content_message = content_message

        if len(content_message) > self.MAX_MESSAGE_LENGTH:
            self._handle_long_message()
        else:
            self._show(window_title, content_message)

    def _show(self, title: str, message: str) -> None:
        """Muestra el diálogo nativo. Debe ser sobrescrito por subclases."""
        raise NotImplementedError

    def _handle_long_message(self) -> None:
        """
        Guarda el mensaje completo en log y presenta un resumen al usuario.
        """
        log_path = ErrorLogger.log(self.window_title, self.content_message)
        summary = self.content_message[:self.MAX_MESSAGE_LENGTH] + "..."

        full_notification = (
            f"{summary}"
            f"El mensaje completo es demasiado extenso para mostrarlo aquí."
            f"Se ha guardado un registro detallado en:"
            f"{log_path}"
        )

        self._show(self.window_title, full_notification)


class PopUp(_BasePopUp):
    """
    Diálogo informativo (icono de información).

    Si el mensaje supera 64 caracteres, se guarda en log y se muestra un resumen.
    """

    def _show(self, title: str, message: str) -> None:
        tk = Tk()
        tk.withdraw()
        messagebox.showinfo(title, message)
        tk.destroy()


class PopUpWarning(_BasePopUp):
    """
    Diálogo de advertencia (icono de advertencia / triángulo amarillo).

    Si el mensaje supera 64 caracteres, se guarda en log y se muestra un resumen.
    """

    def _show(self, title: str, message: str) -> None:
        tk = Tk()
        tk.withdraw()
        messagebox.showwarning(title, message)
        tk.destroy()


class PopUpError(_BasePopUp):
    """
    Diálogo de error crítico (icono de error / X roja).

    Si el mensaje supera 64 caracteres, se guarda en log y se muestra un resumen.
    """

    def _show(self, title: str, message: str) -> None:
        tk = Tk()
        tk.withdraw()
        messagebox.showerror(title, message)
        tk.destroy()
