# client.py
"""
Cliente MCP simple para modelo IA
Usa tu script de conexión para hablar con el modelo.
Usa FastMCP para llamar a la herramienta en server.py.
"""
import sys
import os
import asyncio

# Añadir el directorio 'src' al path para permitir imports relativos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 🔧 Importamos funciones de los otros módulos
from src.chat_modelo_local import (cargar_mensajes, crear_payload, hacer_solicitud_http_al_modelo, limitar_historial_inteligente, openrouter_connect)
from src.mcp_manual import (debe_usar_tool, extraer_argumentos_necesarios_herramienta, ejecutar_tool_manual, agregar_al_historial_simulando_call_tool)
from src.contrato_y_payload import (lectura_contrato_tools, payload_para_modelo_con_herramientas)
from src.procesamiento_respuesta import (extraer_mensaje_modelo, extraer_contenido, imprimir_estructura_mensaje_enviado)
from src.historial_y_contexto import (guardar_historial, crear_contexto_temporal)


async def main(herramienta_server_mcp: str) -> None:
    """
    Función principal que orquesta la ejecución del cliente MCP.

    Flujo de ejecución:
    1.  Carga el contrato de herramientas desde un archivo JSON.
    2.  Carga el historial previo de mensajes desde 'contexto/mensaje_modelo.json'.
    3.  Inyecta dinámicamente el mensaje del usuario con la herramienta solicitada.
    4.  Establece conexión con OpenRouter usando tu API key.
    5.  Prepara el payload con las herramientas disponibles.
    6.  Envía la solicitud al modelo.
    7.  Extrae el mensaje del modelo de la respuesta.
    8.  Muestra la estructura del mensaje para depuración.
    9.  Detecta si el modelo quiere usar la herramienta.
    10. Si se detecta intención, llama a la herramienta manualmente vía MCP.
    11. Obtiene los argumentos necesarios para la herramienta.
    12. Ejecuta la herramienta y obtiene el resultado.
    13. Simula un tool_call en el historial con el resultado de la herramienta.
    14. Prepara una segunda llamada al modelo con el resultado de la tool.
    15. Envía la segunda solicitud al modelo.
    16. Extrae la respuesta final del modelo.
    17. Muestra la respuesta final en consola.
    18. Agrega la respuesta final al historial.
    19. Limita el historial para evitar crecimiento infinito.
    20. Guarda el historial actualizado en disco.
    21. Elimina el archivo temporal para mantener el estado limpio.
    """
    # === Crear contexto temporal y cargar mensajes iniciales ===
    # Se copia la plantilla de contexto a un archivo temporal.
    # Esto asegura que el archivo original no se modifique.
    ruta_temporal = crear_contexto_temporal()
    mensajes = cargar_mensajes(str(ruta_temporal))

    # === Inyectar el mensaje del usuario con la herramienta solicitada ===
    # El nombre de la herramienta se inyecta dinámicamente para guiar al modelo.
    mensajes.append({
        "role": "user",
        "content": f"Herramienta '{herramienta_server_mcp}'"
    })

    # === 1. Cargar contrato de herramientas desde archivo JSON ===
    # El contrato define qué herramientas están disponibles y cómo se llaman.
    # Es necesario para incluir 'tools' en el payload, aunque el modelo no las use nativamente.
    contrato_tools = lectura_contrato_tools()
    if not contrato_tools:
        print("Error: No se pudo cargar el contrato de las tools.")
        return

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
    # imprimir_estructura_mensaje_enviado(mensaje)

    # === 8. Detectar intención de usar herramienta ===
    # Se analiza el contenido del mensaje para detectar si el modelo quiere
    # usar la herramienta, incluso si no genera tool_calls.
    # Se usa detección por palabras clave y contexto.
    if debe_usar_tool(contenido, nombre_tool=herramienta_server_mcp, palabras_clave=[]):
        # === Cambiar el system prompt para la fase de respuesta final ===
        # Una vez detectada la herramienta, el modelo debe responder útilmente.
        mensajes[0] = {
            "role": "system",
            "content": "Eres un asistente útil. Usa el contexto para responder."
        }
        print(f"Se detectó intención de usar '{herramienta_server_mcp}'. Llamando a server.py...")

        try:
            # === 11. Ejecutar herramienta genérica vía FastMCP ===
            # Se conecta al servidor MCP (server.py) y se llama a la herramienta.
            # Los argumentos se extraen dinámicamente según la herramienta.
            resultado_completo = await ejecutar_tool_manual(
                nombre_tool=herramienta_server_mcp,
                argumentos=extraer_argumentos_necesarios_herramienta(herramienta_server_mcp, mensajes)
            )

            # === 12. Simular tool_call en el historial ===
            # Se agrega el resultado de la herramienta al historial en el formato
            # esperado por el modelo (role: 'tool'), simulando un tool_call real.
            agregar_al_historial_simulando_call_tool(mensajes, herramienta_server_mcp, tool_call_id="manual-1", resultado=resultado_completo["result"])

            # === 13. Preguntar por el resultado (¡nueva intención!) ===
            # Se fuerza una nueva interacción para que el modelo interprete el resultado.
            mensajes.append({
                "role": "user",
                "content": "¿Qué resultado se obtuvo?"
            })

            # === 14. Preparar segunda llamada con resultado de la tool ===
            # Se crea un nuevo payload con el historial actualizado,
            # incluyendo el resultado de la herramienta.
            payload_final = crear_payload(mensajes, "mistral")
            response_final = hacer_solicitud_http_al_modelo(url, headers, payload_final)

            # === 15. Extraer respuesta final del modelo ===
            # El modelo ahora puede usar el resultado de la herramienta
            # para generar una respuesta coherente.
            respuesta_final = extraer_contenido(response_final)
            print("✅ Respuesta final:", respuesta_final)

            # === 16. Agregar respuesta final al historial ===
            # Se guarda la respuesta final para mantener la conversación.
            mensajes.append({"role": "assistant", "content": respuesta_final})

            # === 17. Limitar historial para evitar crecimiento ===
            # Se mantienen solo los últimos intercambios relevantes
            # para no saturar el contexto ni el archivo.
            mensajes = limitar_historial_inteligente(mensajes, max_intercambios=5)

            # === 18. Guardar historial actualizado ===
            # Se guarda el historial en disco para mantener la memoria
            # entre ejecuciones del cliente.
            guardar_historial(mensajes)

            # === Final del script: limpiar archivo temporal ===
            # Se elimina el archivo temporal para asegurar que la próxima
            # ejecución comience con una copia limpia de la plantilla.
            if ruta_temporal.exists():
                os.remove(ruta_temporal)
                print("🗑️ Archivo temporal eliminado. Listo para la próxima ejecución.")

        except Exception as e:
            print(f"Error al ejecutar la tool: {e}")

    else:
        # === 17. Caso: no se detectó intención de usar herramienta ===
        # El modelo no mostró interés en usar herramientas.
        # Se finaliza sin invocar MCP.
        print("El modelo no quiso usar ninguna tool.")


if __name__ == "__main__":
    asyncio.run(main("suma"))