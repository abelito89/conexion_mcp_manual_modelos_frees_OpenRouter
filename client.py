# mcp_simple.py
"""
Cliente MCP simple para modelo IA
Usa tu script de conexión para hablar con el modelo.
Usa FastMCP para llamar a la tool 'hola_mundo_mcp' en server.py.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
import asyncio
# 🔧 Importamos funciones de los otros módulos
from src.chat_modelo_local import (cargar_mensajes, crear_payload, hacer_solicitud_http_al_modelo, limitar_historial_inteligente, openrouter_connect)
from src.mcp_manual import (debe_usar_hola_mundo_mcp, ejecutar_hola_mundo_mcp_manual, agregar_al_historial_simulando_call_tool)
from src.contrato_y_payload import (lectura_contrato_tools, payload_para_modelo_con_herramientas)
from src.procesamiento_respuesta import (extraer_mensaje_modelo, extraer_contenido, imprimir_estructura_mensaje_enviado)
from src.historial_y_contexto import(extraer_mensaje_usuario, guardar_historial)
from pathlib import Path


async def main():
    """Función principal que orquesta la ejecución del cliente MCP.
    Realiza los siguientes pasos:
    1. Carga el contrato de herramientas desde un archivo JSON.
    2. Carga el historial previo de mensajes desde 'mensaje_modelo.json'.
    3. Establece conexión con OpenRouter usando tu API key.
    4. Prepara el payload con las herramientas y el historial.
    5. Envía la solicitud al modelo.
    6. Extrae el mensaje del modelo de la respuesta.
    7. Muestra la estructura del mensaje para depuración.
    8. Detecta si el modelo quiere usar la herramienta 'hola_mundo_mcp'.
    9. Si se detecta intención, llama a la herramienta manualmente vía MCP.
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
    # === 1. Cargar contrato de herramientas ===
    contrato_tools = lectura_contrato_tools()
    if not contrato_tools:
        print("Error: No se pudo cargar el contrato de las tools.")
        return

    # === 2. Cargar historial previo ===
    ruta_actual = Path(".")
    ruta_contexto = ruta_actual / "contexto/mensaje_modelo.json"
    mensajes = cargar_mensajes(str(ruta_contexto))

    # === 3. Establecer conexión con OpenRouter ===
    url, headers = openrouter_connect()

    # === 4. Preparar payload con herramientas ===
    payload_con_herramientas = payload_para_modelo_con_herramientas(mensajes, contrato_tools)

    # === 5. Enviar solicitud al modelo ===
    print("Enviando a al modelo...")
    response = hacer_solicitud_http_al_modelo(url, headers, payload_con_herramientas)

    if response.status_code != 200:
        print("Error:", response.text)
        return

    # === 6. Extraer mensaje del modelo ===
    mensaje = extraer_mensaje_modelo(response)

    # === 7. Mostrar estructura para depuración ===
    imprimir_estructura_mensaje_enviado(mensaje)

    # === 8. Detectar intención de usar herramienta ===
    if debe_usar_hola_mundo_mcp(mensaje.get("content", "")):
        print("Se detectó intención de usar 'hola_mundo_mcp'. Llamando a server.py...")

        # === 9. Obtener último mensaje del usuario para contexto ===
        ultimo_mensaje_usuario = extraer_mensaje_usuario(mensajes)

        try:
            # === 10. Ejecutar herramienta manualmente vía MCP ===
            resultado = await ejecutar_hola_mundo_mcp_manual(ultimo_mensaje_usuario)

            # === 11. Simular tool_call en el historial ===
            agregar_al_historial_simulando_call_tool(
                mensajes, "hola_mundo_mcp", "manual-1", resultado
            )

            # === 12. Preparar segunda llamada con resultado de la tool ===
            payload_final = crear_payload(mensajes, "mistral")
            response_final = hacer_solicitud_http_al_modelo(url, headers, payload_final)

            # === 13. Extraer respuesta final del modelo ===
            respuesta_final = extraer_contenido(response_final)
            print("✅ Respuesta final:", respuesta_final)

            # === 14. Agregar respuesta final al historial ===
            mensajes.append({"role": "assistant", "content": respuesta_final})

            # === 15. Limitar historial para evitar crecimiento ===
            mensajes = limitar_historial_inteligente(mensajes, max_intercambios=5)

            # === 16. Guardar historial actualizado ===
            guardar_historial(mensajes)

        except Exception as e:
            print(f"Error al ejecutar la tool: {e}")

    else:
        # === 17. Caso: no se detectó intención de usar herramienta ===
        print("El modelo no quiso usar ninguna tool.")


if __name__ == "__main__":
    asyncio.run(main())