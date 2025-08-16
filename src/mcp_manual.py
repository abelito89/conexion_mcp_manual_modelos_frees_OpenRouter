import json
import sys
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport
import datetime
from datetime import datetime


def debe_usar_tool(texto: str, nombre_tool: str, palabras_clave: list[str] | None = None) -> bool:
    """
    Detecta si el modelo quiere usar una herramienta específica.
    Comprueba tanto palabras clave personalizadas como patrones de acción genéricos.
    No distingue entre mayúsculas y minúsculas.
    
    Args:
        texto (str): El contenido de la respuesta del modelo.
        nombre_tool (str): Nombre exacto de la herramienta (ej: 'hola_mundo_mcp').
        palabras_clave (list[str] | None): Lista opcional de frases o palabras clave personalizadas.
    
    Returns:
        bool: True si se detecta intención de usar la herramienta, False en caso contrario.
    """
    if not texto or not texto.strip():
        return False

    # Normalizar: convertir todo a minúsculas
    texto = texto.lower().strip()
    nombre_tool = nombre_tool.lower().strip()

    # 1. Si se pasan palabras clave, usarlas primero (en minúsculas)
    if palabras_clave:
        for palabra in palabras_clave:
            if palabra.lower().strip() in texto:
                return True

    # 2. Palabras clave por defecto (todas en minúsculas por construcción)
    claves_por_defecto = [
        f"{nombre_tool}",
        f"voy a usar {nombre_tool}",
        f"voy a usar la herramienta {nombre_tool}",  # ← faltaba coma antes
        f"usaré {nombre_tool}",
        f"procedo a usar {nombre_tool}",
        f"ejecutaré {nombre_tool}",
        f"llamaré a {nombre_tool}",
        f"activaré {nombre_tool}",
        f"quiero usar {nombre_tool}",
        f"es {nombre_tool}"
    ]

    for clave in claves_por_defecto:
        if clave in texto:
            return True

    # 3. Como respaldo: ¿menciona la herramienta en contexto de herramientas?
    contexto_herramientas = [
        "usar herramienta",
        "ejecutar herramienta",
        "llamar a la herramienta",
        "activar herramienta"
    ]
    if nombre_tool in texto:
        for contexto in contexto_herramientas:
            if contexto in texto:
                return True

    return False



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