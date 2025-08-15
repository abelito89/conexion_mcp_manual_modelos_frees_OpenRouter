import json
from requests import Response


def extraer_mensaje_modelo(response: Response) -> dict:
    """Crea un payload que incluye herramientas y fuerza su uso.
    Prepara la solicitud para que el modelo considere activar una tool.

    Args:
        response (Response): Respuesta del modelo tras la solicitud HTTP.

    Returns:
        dict: Diccionario con el mensaje del modelo.
        Contiene el contenido del mensaje y otros metadatos.
    """
    data = response.json()
    mensaje = data["choices"][0]["message"]
    return mensaje


def extraer_contenido(response_final: Response) -> str:
    """Extrae solo el contenido textual (campo 'content') de la respuesta del modelo.
    Útil para mostrar o guardar la respuesta final.

    Args:
        response_final (Response): Respuesta final del modelo tras la segunda llamada.

    Returns:
        str: Contenido textual de la respuesta del modelo.
        Si no se encuentra el campo 'content', retorna una cadena vacía.
    """
    final_data = response_final.json()
    respuesta_final = final_data["choices"][0]["message"]["content"]
    return respuesta_final


def imprimir_estructura_mensaje_enviado(mensaje: dict) -> None:
    """Método que muestra en consola la estructura completa del mensaje del modelo.
    Ayuda en depuración para ver si hay tool_calls o contenido inesperado.

    Args:
        mensaje (dict): Mensaje del modelo que queremos mostrar.
    """
    print("\n=== ESTRUCTURA DE 'mensaje' ===")
    print(json.dumps(mensaje, indent=2, ensure_ascii=False))
    print("================================\n")
    print("El modelo dice:", mensaje.get("content") or "(sin texto)")