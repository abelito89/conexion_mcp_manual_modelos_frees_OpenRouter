import json
from chat_modelo_local import crear_payload
from pathlib import Path
from logging_mcp import error

ruta_actual = Path(".")
ruta_raiz = ruta_actual.parent
ruta_contrato_tools = ruta_raiz / "contexto/contrato_tools.json"



def lectura_contrato_tools() -> list:
    """
    Lee el contrato de herramientas desde el archivo JSON.
    Este contrato es una lista de definiciones de herramientas.

    Returns:
        list: Lista de diccionarios con la definición de cada herramienta.
        Si hay error, retorna una lista vacía.
    """
    try:
        with open(str(ruta_contrato_tools), "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        error(f"Error al leer contrato_tools.json: {e}")
        return []
    


def payload_para_modelo_con_herramientas(mensajes: list, contrato_tools: list) -> dict:
    """
    Crea un payload que incluye una lista de herramientas y fuerza su uso.
    
    Args:
        mensajes (list): Historial de mensajes.
        contrato_tools (list): Lista de herramientas disponibles.
    
    Returns:
        dict: Payload listo para enviar al modelo.
    """
    payload_con_herramientas = crear_payload(mensajes, "mistral")
    payload_con_herramientas["tools"] = contrato_tools  # ← ahora es una lista
    
    return payload_con_herramientas