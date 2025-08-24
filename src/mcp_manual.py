import json
import sys
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport
import datetime
from datetime import datetime
from historial_y_contexto import extraer_mensaje_usuario
from logging_mcp import warning, info, success, separator, debug


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
    debug("=== DETECCIÓN DE INTENCIÓN ===")
    debug(f"Texto recibido: {texto}")
    debug(f"Herramienta buscada: {nombre_tool}")
    
    if not texto or not texto.strip():
        debug("❌ Texto vacío o solo espacios")
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
        f"voy a usar la herramienta {nombre_tool}",
        f"usaré {nombre_tool}",
        f"procedo a usar {nombre_tool}",
        f"ejecutaré {nombre_tool}",
        f"llamaré a {nombre_tool}",
        f"activaré {nombre_tool}",
        f"quiero usar {nombre_tool}",
        f"es {nombre_tool}"
    ]

    debug("🔍 Buscando coincidencias en claves por defecto:")
    for clave in claves_por_defecto:
        debug(f"   Comprobando: '{clave}'")
        if clave in texto:
            debug(f"✅ Coincidencia encontrada con: '{clave}'")
            return True
    debug("❌ No se encontraron coincidencias en claves por defecto")

    # 3. Como respaldo: ¿menciona la herramienta en contexto de herramientas?
    contexto_herramientas = [
        "usar herramienta",
        "ejecutar herramienta",
        "llamar a la herramienta",
        "activar herramienta"
    ]
    debug("🔍 Verificando mención de herramienta en contexto...")
    if nombre_tool in texto:
        debug("✅ Herramienta mencionada en el texto")
        for contexto in contexto_herramientas:
            debug(f"   Comprobando contexto: '{contexto}'")
            if contexto in texto:
                debug(f"✅ Encontrado contexto válido: '{contexto}'")
                return True
        debug("❌ Herramienta mencionada pero sin contexto válido")
    else:
        debug("❌ Herramienta no mencionada en el texto")

    debug("❌ No se detectó intención de usar la herramienta")
    return False


def extraer_argumentos_necesarios_herramienta(herramienta_server_mcp:str, mensajes:list) -> dict:
    """Extrae los argumentos que necesita la herramienta invocada

    Args:
        herramienta_server_mcp (str): Nombre de la herramienta cuyos argumentos se desea extraer
        mensajes (list): Lista de mensajes del historial de conversación.

    Returns:
        dict: Diccionario con los nombres de los argumentos como llaves y sus valores como vaalores
    """

    if herramienta_server_mcp == "hola_mundo_mcp":
        ultimo_mensaje_usuario = extraer_mensaje_usuario(mensajes)
        mensaje_a_enviar = input(f"Introduce el mensaje a enviar: ")
        # === 10. Ejecutar herramienta genérica vía FastMCP ===
        # Se conecta al servidor MCP (server.py) y se llama a la herramienta.
        # El resultado se devuelve en formato serializable.
        argumentos_tool = {"mensaje": mensaje_a_enviar}
    elif herramienta_server_mcp == "suma":
        numero1 = int(input(f"Introduce el primer número: "))
        numero2 = int(input(f"Introduce el segundo número: "))
        argumentos_tool = {"numero1": numero1, "numero2": numero2}

    else:
# Para cualquier otra herramienta, puedes manejarla aquí
        warning(f"⚠️ No se conocen los argumentos para '{herramienta_server_mcp}'")
        return {}
    return argumentos_tool



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

def resumen_ejecucion(herramienta_server_mcp,argumentos_tool, resultado_completo):
    separator()
    success("Ejecución completada")
    info(f"   Herramienta: {herramienta_server_mcp}")
    info(f"   Entrada: {argumentos_tool}")  # o ajusta según la herramienta
    info(f"   Resultado: {resultado_completo['result']}")
    info(f"   Hora: {datetime.now().strftime('%H:%M:%S')}")