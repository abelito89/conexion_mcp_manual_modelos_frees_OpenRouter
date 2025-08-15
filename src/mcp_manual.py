import json
import sys
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport
import datetime


def debe_usar_tool(texto: str, nombre_tool: str, palabras_clave: list[str] | None = None) -> bool:
    """
    Detecta si el texto del modelo indica que quiere usar una herramienta específica.
    
    Args:
        texto (str): El contenido de la respuesta del modelo.
        nombre_tool (str): Nombre de la herramienta (ej: 'hola_mundo_mcp').
        palabras_clave (list[str] | None): Lista de frases o palabras clave asociadas.
    
    Returns:
        bool: True si se detecta intención de usar la herramienta.
    """
    if not texto or not texto.strip():
        return False

    texto = texto.lower()

    # Palabras clave por defecto si no se pasan
    claves = palabras_clave or []
    if not claves:
        claves = [
            f"usar {nombre_tool}",
            f"ejecutar {nombre_tool}",
            f"llamar a {nombre_tool}",
            "usar herramienta",
            "ejecutar herramienta",
            "llamar a la herramienta"
        ]

    # Buscar cualquier palabra clave en el texto
    return any(palabra in texto for palabra in claves)



async def ejecutar_tool_manual(nombre_tool: str, argumentos: dict, script_path: str = "server.py") -> dict:
    """
    Ejecuta una herramienta MCP manualmente a través del servidor.
    
    Args:
        nombre_tool (str): Nombre de la herramienta a ejecutar.
        argumentos (dict): Argumentos que se pasan a la herramienta.
        script_path (str): Ruta al script del servidor MCP.
    
    Returns:
        dict: Resultado de la herramienta, serializable a JSON.
    """
    transport = PythonStdioTransport(script_path=script_path, python_cmd=sys.executable)
    
    async with Client(transport) as client:
        resultado = await client.call_tool(nombre_tool, argumentos)
    
    # Retorna un dict plano para poder hacer json.dumps()
    return {
        "tool_name": nombre_tool,
        "result": {k: v.isoformat() if isinstance(v, datetime) else v 
                   for k, v in resultado.data.__dict__.items()}
    }


def agregar_al_historial_simulando_call_tool(mensajes: list, tool_name: str, tool_call_id: str, resultado: dict) -> None:
    """Método que simula un tool_call real agregando el resultado de la herramienta al historial. 
    Usa el formato esperado por el modelo (role: 'tool').

    Args:
        mensajes (list): Lista de mensajes del historial de conversación.
        tool_name (str): Nombre de la herramienta que se está simulando.
        tool_call_id (str): ID único de la llamada a la herramienta (puede ser 'manual-1' o similar).
        resultado (dict): Resultado de la herramienta que queremos agregar al historial.
    """
    mensajes.append({
        "role": "tool",
        "name": tool_name,
        "tool_call_id": tool_call_id,
        "content": json.dumps(resultado, ensure_ascii=False)
    })