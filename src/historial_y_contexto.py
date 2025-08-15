import json
from pathlib import Path


ruta_actual = Path(".")
ruta_raiz = ruta_actual.parent
ruta_mensaje_modelo = ruta_raiz / "contexto/mensaje_modelo.json"

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



def guardar_historial(mensajes: list) -> None:
    """Método que guarda el historial actual de mensajes en un archivo JSON.
    Mantiene la memoria entre ejecuciones del cliente.
    Esto permite que el modelo "recuerde" la conversación previa.
    Args:
        mensajes (list): Lista de mensajes del historial de conversación.
    Returns:
        None: No retorna nada, solo guarda el historial en 'mensaje_modelo.json' con formato JSON.
    """
    with open(str(ruta_mensaje_modelo), "w", encoding="utf-8") as f:
        json.dump(mensajes, f, indent=2, ensure_ascii=False)