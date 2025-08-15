import json
from chat_modelo_local import crear_payload
from pathlib import Path

ruta_actual = Path(".")
ruta_raiz = ruta_actual.parent
ruta_contrato_tools = ruta_raiz / "contexto/contrato_tools.json"

def lectura_contrato_tools() -> dict:
    """Lee el contrato de herramientas desde el archivo JSON.
    Este contrato describe qué herramientas están disponibles para el modelo.

    Returns:
        dict: Diccionario con la definición de las herramientas.
        Si no se encuentra el archivo o hay un error, retorna un diccionario vacío.
    """
    with open(str(ruta_contrato_tools), "r", encoding="utf-8") as f:
        return json.load(f)  # Solo una tool: 'hola_mundo_mcp'
    


def payload_para_modelo_con_herramientas(mensajes: list, contrato_tools: dict) -> dict:
    """Crea un payload que incluye herramientas y fuerza su uso.
    Prepara la solicitud para que el modelo considere activar una tool.

    Args:
        mensajes (list): Lista de mensajes del historial de conversación.
        contrato_tools (dict): Definición de las herramientas disponibles.

    Returns:
        dict: Payload listo para enviar al modelo.
        Incluye herramientas y especifica que se debe elegir una tool.
    """
    payload_con_herramientas = crear_payload(mensajes, "mistral")
    payload_con_herramientas["tools"] = contrato_tools
    payload_con_herramientas["tool_choice"] = "required"  # Mistral sí respeta esto
    return payload_con_herramientas