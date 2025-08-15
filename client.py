# client.py
"""
Cliente MCP simple para modelo IA
Usa tu script de conexión para hablar con el modelo.
Usa FastMCP para llamar a la tool 'hola_mundo_mcp' en server.py.
"""
import sys
import os
import asyncio
from pathlib import Path

# Añadir el directorio 'src' al path para permitir imports relativos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 🔧 Importamos funciones de los otros módulos
from src.chat_modelo_local import (cargar_mensajes, crear_payload, hacer_solicitud_http_al_modelo, limitar_historial_inteligente, openrouter_connect)
from src.mcp_manual import (debe_usar_tool, ejecutar_tool_manual, agregar_al_historial_simulando_call_tool)
from src.contrato_y_payload import (lectura_contrato_tools, payload_para_modelo_con_herramientas)
from src.procesamiento_respuesta import (extraer_mensaje_modelo, extraer_contenido, imprimir_estructura_mensaje_enviado)
from src.historial_y_contexto import (extraer_mensaje_usuario, guardar_historial)


async def main():
    """
    Función principal que orquesta la ejecución del cliente MCP.

    Flujo de ejecución:
    1.  Carga el contrato de herramientas desde un archivo JSON.
    2.  Carga el historial previo de mensajes desde 'contexto/mensaje_modelo.json'.
    3.  Establece conexión con OpenRouter usando tu API key.
    4.  Prepara el payload con las herramientas disponibles.
    5.  Envía la solicitud al modelo.
    6.  Extrae el mensaje del modelo de la respuesta.
    7.  Muestra la estructura del mensaje para depuración.
    8.  Detecta si el modelo quiere usar la herramienta 'hola_mundo_mcp'.
    9.  Si se detecta intención, llama a la herramienta manualmente vía MCP.
    10. Obtiene el último mensaje del usuario para contexto.
    11. Ejecuta la herramienta y obtiene el resultado.
    12. Simula un tool_call en el historial con el resultado de la herramienta.
    13. Prepara una segunda llamada al modelo con el resultado de la tool.
    14. Envía la segunda solicitud al modelo.
    15. Extrae la respuesta final del modelo.
    16. Muestra la respuesta final en consola.
    17. Agrega la respuesta final al historial.
    18. Limita el historial para evitar crecimiento infinito.
    19. Guarda el historial actualizado en 'mensaje_modelo.json'.
    """
    # === 1. Cargar contrato de herramientas desde archivo JSON ===
    # El contrato define qué herramientas están disponibles y cómo se llaman.
    # Es necesario para incluir 'tools' en el payload, aunque el modelo no las use nativamente.
    contrato_tools = lectura_contrato_tools()
    if not contrato_tools:
        print("Error: No se pudo cargar el contrato de las tools.")
        return

    # === 2. Cargar historial previo de mensajes ===
    # Se carga el historial desde un archivo JSON en la carpeta 'contexto'.
    # Este historial incluye el system prompt y el contexto de la conversación.
    ruta_actual = Path(".")
    ruta_contexto = ruta_actual / "contexto/mensaje_modelo.json"
    mensajes = cargar_mensajes(str(ruta_contexto))

    # === 3. Establecer conexión con OpenRouter ===
    # Se obtienen la URL y las cabeceras necesarias para autenticarse con la API.
    # Usa la API key definida en .env.
    url, headers = openrouter_connect()

    # === 4. Preparar payload con herramientas ===
    # Se construye el payload incluyendo el historial y el contrato de herramientas.
    # Aunque el modelo no use tool_calls, se incluye para mantener compatibilidad MCP.
    payload_con_herramientas = payload_para_modelo_con_herramientas(mensajes, contrato_tools)

    # === 5. Enviar solicitud al modelo ===
    # Se envía la solicitud a través de la API de OpenRouter.
    # El modelo puede responder con texto o, en teoría, con tool_calls.
    print("Enviando a al modelo...")
    response = hacer_solicitud_http_al_modelo(url, headers, payload_con_herramientas)

    if response.status_code != 200:
        print("Error:", response.text)
        return

    # === 6. Extraer mensaje del modelo ===
    # Se extrae el mensaje principal de la respuesta del modelo.
    # Este mensaje contiene 'role', 'content' y posiblemente 'tool_calls'.
    mensaje = extraer_mensaje_modelo(response)
    contenido = mensaje.get("content", "").strip()

    # === 7. Mostrar estructura para depuración ===
    # Se imprime el mensaje completo en formato JSON para verificar si hay tool_calls.
    # Útil para diagnosticar por qué se activa o no la herramienta.
    imprimir_estructura_mensaje_enviado(mensaje)

    # === 8. Detectar intención de usar herramienta ===
    # Se analiza el contenido del mensaje para detectar si el modelo quiere
    # usar la herramienta 'hola_mundo_mcp', incluso si no genera tool_calls.
    # Se usa detección por palabras clave y contexto.
    if debe_usar_tool(
        contenido,
        nombre_tool="hola_mundo_mcp",
        palabras_clave=["hola desde cuba", "enviar saludo", "mensaje especial"]
    ):
        print("Se detectó intención de usar 'hola_mundo_mcp'. Llamando a server.py...")

        # === 9. Obtener último mensaje del usuario para contexto ===
        # Se extrae el último mensaje del usuario para decidir qué argumentos
        # enviar a la herramienta (por ejemplo, detectar si mencionó "Cuba").
        ultimo_mensaje_usuario = extraer_mensaje_usuario(mensajes)
        mensaje_a_enviar = "Hola desde Cuba" if "cuba" in ultimo_mensaje_usuario.lower() else "Hola"

        try:
            # === 10. Ejecutar herramienta genérica vía FastMCP ===
            # Se conecta al servidor MCP (server.py) y se llama a la herramienta.
            # El resultado se devuelve en formato serializable.
            resultado_completo = await ejecutar_tool_manual(
                nombre_tool="hola_mundo_mcp",
                argumentos={"mensaje": mensaje_a_enviar}
            )

            # === 11. Simular tool_call en el historial ===
            # Se agrega el resultado de la herramienta al historial en el formato
            # esperado por el modelo (role: 'tool'), simulando un tool_call real.
            agregar_al_historial_simulando_call_tool(
                mensajes,
                tool_name="hola_mundo_mcp",
                tool_call_id="manual-1",
                resultado=resultado_completo["result"]
            )

            # === 12. Preparar segunda llamada con resultado de la tool ===
            # Se crea un nuevo payload con el historial actualizado,
            # incluyendo el resultado de la herramienta.
            payload_final = crear_payload(mensajes, "mistral")
            response_final = hacer_solicitud_http_al_modelo(url, headers, payload_final)

            # === 13. Extraer respuesta final del modelo ===
            # El modelo ahora puede usar el resultado de la herramienta
            # para generar una respuesta coherente.
            respuesta_final = extraer_contenido(response_final)
            print("✅ Respuesta final:", respuesta_final)

            # === 14. Agregar respuesta final al historial ===
            # Se guarda la respuesta final para mantener la conversación.
            mensajes.append({"role": "assistant", "content": respuesta_final})

            # === 15. Limitar historial para evitar crecimiento ===
            # Se mantienen solo los últimos intercambios relevantes
            # para no saturar el contexto ni el archivo.
            mensajes = limitar_historial_inteligente(mensajes, max_intercambios=5)

            # === 16. Guardar historial actualizado ===
            # Se guarda el historial en disco para mantener la memoria
            # entre ejecuciones del cliente.
            guardar_historial(mensajes)

        except Exception as e:
            print(f"Error al ejecutar la tool: {e}")

    else:
        # === 17. Caso: no se detectó intención de usar herramienta ===
        # El modelo no mostró interés en usar herramientas.
        # Se finaliza sin invocar MCP.
        print("El modelo no quiso usar ninguna tool.")


if __name__ == "__main__":
    asyncio.run(main())