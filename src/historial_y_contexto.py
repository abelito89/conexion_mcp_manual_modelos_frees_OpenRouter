import json
from pathlib import Path
import os
from shutil import copyfile


ruta_actual = Path(".")
ruta_raiz = ruta_actual.parent
ruta_mensaje_modelo = ruta_raiz / "contexto/mensaje_modelo.json"


def crear_contexto_temporal() -> Path:
    """Método que crea un contexto temporal para la conversación.

    Returns:
        Path: Ruta al archivo de contexto temporal creado.
    """
    # Rutas
    ruta_plantilla = Path("contexto") / "mensaje_modelo.json"
    ruta_temporal = Path("contexto") / "temp_context.json"

    # === 1. Si existe el temporal, borrarlo (por si queda de antes)
    if ruta_temporal.exists():
        os.remove(ruta_temporal)

    # === 2. Copiar la plantilla al archivo temporal
    copyfile(ruta_plantilla, ruta_temporal)
    return ruta_temporal


def extraer_mensaje_usuario(mensajes: list) -> str:
    """Busca y devuelve el último mensaje del usuario en el historial.
    Útil para decidir qué parámetros enviar a una herramienta.

    Args:
        mensajes (list): Lista de mensajes del historial de conversación.

    Returns:
        str: Último mensaje del usuario encontrado en el historial.
        Si no hay mensajes de usuario, retorna una cadena vacía.
    """
    for msg in reversed(mensajes):
        if msg["role"] == "user":
            return msg["content"]
    return ""  # Si no hay mensajes de usuario, devuelve cadena vacía



def guardar_historial(mensajes: list, archivo: str = "contexto/historial_temp.json") -> None:
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(mensajes, f, indent=2, ensure_ascii=False)