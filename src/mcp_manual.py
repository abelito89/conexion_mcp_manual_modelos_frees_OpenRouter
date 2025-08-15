import json
import sys
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport


def debe_usar_hola_mundo_mcp(texto: str) -> bool:
    """Detecta si el texto del modelo indica que quiere usar la herramienta 'hola_mundo_mcp'.
    Es una detección por palabras clave.

    Args:
        texto (str): Texto del modelo que queremos analizar.

    Returns:
        bool: True si el texto sugiere usar la herramienta, False en caso contrario.
    """
    if not texto:
        return False
    texto = texto.lower()
    palabras_clave = [
        "hola_mundo_mcp",
        "usar herramienta",
        "ejecutar herramienta",
        "hola desde cuba"
    ]
    return any(palabra in texto for palabra in palabras_clave)


async def ejecutar_hola_mundo_mcp_manual(mensaje_usuario: str) -> dict:
    """Llama manualmente a la herramienta 'hola_mundo_mcp' a través del servidor MCP.
    Extrae el mensaje adecuado del input del usuario.
    Retorna el resultado formateado para JSON.

    Args:
        mensaje_usuario (str): Mensaje del usuario que se usará como input para la herramienta.

    Returns:
        dict: Resultado de la herramienta formateado como dict.
    """
    # 1. Decide qué mensaje enviar a la herramienta
    mensaje_a_enviar = "Hola desde Cuba" if "cuba" in mensaje_usuario.lower() else "Hola"
    
    # 2. Crea conexión con el servidor MCP (server.py)
    transport = PythonStdioTransport(script_path="server.py", python_cmd=sys.executable)
    
    # 3. Se conecta y llama a la herramienta REAL
    async with Client(transport) as client:
        resultado = await client.call_tool("hola_mundo_mcp", {"mensaje": mensaje_a_enviar})
        # ↑ Esto ejecuta el código de server.py
    
    # 4. Formatea el resultado para que el modelo lo entienda
    return {
        "mensaje": resultado.data.mensaje,
        "timestamp": resultado.data.timestamp.isoformat()
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