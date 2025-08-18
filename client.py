# client.py
"""
Cliente MCP simple para modelo IA
Usa tu script de conexión para hablar con el modelo.
Usa FastMCP para llamar a la herramienta en server.py.
"""
import sys
import os

# Añadir el directorio 'src' al path para permitir imports relativos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 🔧 Importamos funciones de los otros módulos
from src.chat_modelo_local import (cargar_mensajes, crear_payload, hacer_solicitud_http_al_modelo, limitar_historial_inteligente, openrouter_connect)
from src.mcp_manual import (debe_usar_tool, extraer_argumentos_necesarios_herramienta, ejecutar_tool_manual, agregar_al_historial_simulando_call_tool, resumen_ejecucion)
from src.contrato_y_payload import (lectura_contrato_tools, payload_para_modelo_con_herramientas)
from src.procesamiento_respuesta import (extraer_mensaje_modelo, extraer_contenido, imprimir_estructura_mensaje_enviado)
from src.historial_y_contexto import (guardar_historial, crear_contexto_temporal)
from src.menu_interactivo import menu_interactivo
from src.logging_mcp import info, success, error, warning, separator


async def main(herramienta_server_mcp: str) -> None:
    """
    Función principal que orquesta la ejecución del cliente MCP.

    Flujo de ejecución:
    1.  Crea un contexto temporal a partir de mensaje_modelo.json.
    2.  Inyecta el mensaje del usuario con la herramienta solicitada.
    3.  Carga el contrato de herramientas.
    4.  Establece conexión con OpenRouter.
    5.  Envia la solicitud al modelo.
    6.  Detecta intención de usar herramienta.
    7.  Si se detecta, ejecuta la herramienta vía FastMCP.
    8.  Simula un tool_call con el resultado.
    9.  Pregunta al modelo "¿Qué sigue?" para encadenar.
    10. Repite hasta que no se detecte más intención.
    11. Muestra la respuesta final y un resumen.
    12. Pausa para que el usuario lea.
    13. Guarda el historial y limpia el temporal.

    Args:
        herramienta_server_mcp (str): Nombre de la herramienta a ejecutar.
    """
    # === 1. Crear contexto temporal y cargar mensajes iniciales ===
    ruta_temporal = crear_contexto_temporal()
    mensajes = cargar_mensajes(str(ruta_temporal))

    # === 2. Inyectar mensaje del usuario ===
    # Este mensaje guía al modelo para que use la herramienta.
    mensajes.append({
        "role": "user",
        "content": f"Herramienta '{herramienta_server_mcp}'"
    })

    # === 3. Cargar contrato de herramientas ===
    contrato_tools = lectura_contrato_tools()
    if not contrato_tools:
        error("Error: No se pudo cargar el contrato de las tools.")
        return

    # === 4. Establecer conexión con OpenRouter ===
    url, headers = openrouter_connect()

    # === 5. BUCLE DE AGENTE AUTÓNOMO: detectar y ejecutar herramientas ===
    # Mientras el modelo indique intención, seguimos ejecutando.
    tool_used = True
    argumentos_tool = None
    resultado_completo = None

    while tool_used:
        # Preparar payload con el historial actualizado
        payload_actual = payload_para_modelo_con_herramientas(mensajes, contrato_tools)

        # Enviar al modelo
        response = hacer_solicitud_http_al_modelo(url, headers, payload_actual)
        if response.status_code != 200:
            error(f"Error {response.status_code}: {response.text.strip()}")
            tool_used = False
            break

        # Extraer mensaje del modelo
        mensaje = extraer_mensaje_modelo(response)
        contenido = mensaje.get("content", "").strip()

        # Detectar intención de usar la herramienta
        if debe_usar_tool(contenido, nombre_tool=herramienta_server_mcp):
            # Cambiar el system prompt para la fase de respuesta útil
            mensajes[0] = {
                "role": "system",
                "content": "Eres un asistente útil. Usa el contexto para responder."
            }
            info(f"Se detectó intención de usar '{herramienta_server_mcp}'. Llamando a server.py...")

            try:
                # Extraer argumentos necesarios
                argumentos_tool = extraer_argumentos_necesarios_herramienta(herramienta_server_mcp, mensajes)

                # Ejecutar herramienta vía FastMCP
                resultado_completo = await ejecutar_tool_manual(
                    nombre_tool=herramienta_server_mcp,
                    argumentos=argumentos_tool
                )

                # Simular tool_call en el historial
                agregar_al_historial_simulando_call_tool(
                    mensajes,
                    herramienta_server_mcp,
                    tool_call_id=f"manual-{len(mensajes)}",
                    resultado=resultado_completo["result"]
                )

                # Preguntar al modelo qué sigue (para encadenamiento)
                mensajes.append({
                    "role": "user",
                    "content": "¿Qué sigue?"
                })

            except Exception as e:
                error(f"Error al ejecutar la herramienta: {e}")
                tool_used = False

        else:
            # No se detectó intención → salir del bucle
            info("✅ No se detectó más intención de usar herramientas. Finalizando encadenamiento.")
            tool_used = False

    # === 6. Extraer respuesta final del modelo ===
    # La última respuesta útil es la que el modelo dio después del último tool_call
    try:
        respuesta_final = extraer_contenido(response)
    except:
        respuesta_final = "No se pudo obtener una respuesta clara del modelo."

    # === 7. Mostrar respuesta final ===
    separator()
    # success(f"✅ Respuesta final: {respuesta_final}")

    # === Mostrar respuesta final solo si es útil ===
    if len(respuesta_final) < 200 or "resultado" in respuesta_final.lower():
        success(f"✅ Respuesta final: {respuesta_final}")
    else:
        success("✅ Ejecución completada. Resultado procesado.")

    # === 8. Mostrar resumen de ejecución (solo si se ejecutó al menos una herramienta) ===
    if 'argumentos_tool' in locals() and 'resultado_completo' in locals() and argumentos_tool and resultado_completo:
        resumen_ejecucion(herramienta_server_mcp, argumentos_tool, resultado_completo)
    else:
        info("ℹ️ No se ejecutó ninguna herramienta en esta interacción.")

    # === 9. Pausa para que el usuario lea antes de volver al menú ===
    input("\n👉 Presiona ENTER para volver al menú...")

    # === 10. Agregar respuesta final al historial ===
    mensajes.append({"role": "assistant", "content": respuesta_final})

    # === 11. Limitar historial para evitar crecimiento infinito ===
    mensajes = limitar_historial_inteligente(mensajes, max_intercambios=5)

    # === 12. Guardar historial actualizado en disco ===
    guardar_historial(mensajes)

    # === 13. Eliminar archivo temporal ===
    if ruta_temporal.exists():
        os.remove(ruta_temporal)
        success("🗑️ Archivo temporal eliminado. Listo para la próxima ejecución.")


# === Punto de entrada del script ===
if __name__ == "__main__":
    menu_interactivo(main)