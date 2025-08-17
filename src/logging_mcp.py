# src/logging_mcp.py
"""
Sistema de logging centralizado para el proyecto MCP.

Este módulo proporciona funciones simples y coloridas para registrar eventos
en consola durante la ejecución del cliente y el servidor MCP.
Está construido sobre el módulo estándar `logging` de Python,
con soporte opcional para colores en terminal mediante `colorama`.

Funcionalidades:
- Niveles estándar: DEBUG, INFO, WARNING, ERROR.
- Mensaje de éxito con icono (✅).
- Separador visual para mejorar la legibilidad.
- Colores automáticos en consola (si está disponible).
- Fácil de importar y usar en cualquier módulo.

Ejemplo de uso:
    from src.logging_mcp import info, success, error, separator

    info("Iniciando cliente MCP...")
    success("Herramienta ejecutada correctamente.")
    error("No se pudo conectar al servidor.")
    separator()
"""

import logging
import sys
from typing import Optional

# Intentar importar colorama para colores en Windows
try:
    from colorama import init, Fore, Style

    init(autoreset=True)  # Resetea el color después de cada print
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False


# === Configuración del formateador con colores (si disponible) ===
class ColoredFormatter(logging.Formatter):
    """
    Formateador personalizado que añade colores según el nivel de log.
    Si colorama no está disponible, imprime sin color.
    """

    # Código ANSI o colorama
    LEVEL_COLORS = {
        "DEBUG": (Fore.CYAN if HAS_COLORAMA else "\033[96m"),
        "INFO": (Fore.LIGHTBLUE_EX if HAS_COLORAMA else "\033[94m"),
        "WARNING": (Fore.YELLOW if HAS_COLORAMA else "\033[93m"),
        "ERROR": (Fore.RED if HAS_COLORAMA else "\033[91m"),
        "CRITICAL": (Fore.LIGHTRED_EX if HAS_COLORAMA else "\033[95m"),
        "SUCCESS": (Fore.GREEN if HAS_COLORAMA else "\033[92m"),
    }

    RESET = Style.RESET_ALL if HAS_COLORAMA else "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        # Añadir color al nivel
        levelname = record.levelname
        color = self.LEVEL_COLORS.get(levelname, self.RESET)

        # Aplicar formato
        log_format = f"{color}%(asctime)s - %(levelname)s - %(message)s{self.RESET}"
        formatter = logging.Formatter(log_format, datefmt="%H:%M:%S")
        return formatter.format(record)


# === Configuración inicial del logger ===
logger = logging.getLogger("MCP")
logger.setLevel(logging.DEBUG)

# Evitar duplicados si se importa múltiples veces
if not logger.handlers:
    # Handler para consola
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(ColoredFormatter())
    logger.addHandler(handler)


# === Funciones de acceso rápido (API pública del módulo) ===
def debug(message: str) -> None:
    """
    Registra un mensaje de depuración.

    Útil para rastrear el flujo del programa durante el desarrollo.

    Args:
        message (str): Mensaje a registrar.
    """
    logger.debug(message)


def info(message: str) -> None:
    """
    Registra un mensaje informativo.

    Usa este nivel para eventos normales del sistema.

    Args:
        message (str): Mensaje a registrar.
    """
    logger.info(message)


def warning(message: str) -> None:
    """
    Registra un mensaje de advertencia.

    Usa este nivel para situaciones inusuales que no son errores.

    Args:
        message (str): Mensaje a registrar.
    """
    logger.warning(message)


def error(message: str) -> None:
    """
    Registra un mensaje de error.

    Usa este nivel cuando algo falla, pero el programa puede continuar.

    Args:
        message (str): Mensaje a registrar.
    """
    logger.error(message)


def success(message: str) -> None:
    """
    Registra un mensaje de éxito con icono ✅.

    Ideal para indicar que una operación crítica se completó.

    Args:
        message (str): Mensaje a registrar.
    """
    logger.log(logging.INFO + 1, f"✅ {message}")


# Añadir nivel personalizado 'SUCCESS' si no existe
if not hasattr(logging, "SUCCESS"):
    logging.addLevelName(logging.INFO + 1, "SUCCESS")


def separator(char: str = "─", length: int = 50, color: Optional[str] = None) -> None:
    """
    Imprime una línea separadora para mejorar la legibilidad del log.

    Args:
        char (str): Carácter usado para la línea. Por defecto: "─".
        length (int): Longitud de la línea. Por defecto: 50.
        color (Optional[str]): Color opcional (solo si colorama está disponible).
                              Usa Fore.COLOR de colorama. Si es None, usa gris.
    """
    default_color = Fore.LIGHTBLACK_EX if HAS_COLORAMA else "\033[90m"
    reset = Style.RESET_ALL if HAS_COLORAMA else "\033[0m"
    selected_color = color or default_color
    line = char * length
    print(f"{selected_color}{line}{reset}", file=sys.stderr)


# === Atajo opcional para limpiar consola ===
def clear() -> None:
    """
    Limpia la pantalla del terminal de forma portable.
    """
    import os

    os.system("cls" if os.name == "nt" else "clear")