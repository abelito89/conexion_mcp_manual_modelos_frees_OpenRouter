import requests
import os
from dotenv import load_dotenv
import json
from typing import Dict, List, Tuple, Any
from pathlib import Path


load_dotenv()

"""
🚀 Chat con Qwen/Mistral usando OpenRouter (sin OpenAI)

Este script permite interactuar con los modelos Qwen (qwen/qwen-turbo), Mistral(mistralai/mistral-7b-instruct) y Mixtral(nousresearch/nous-hermes-2-mixtral-8x7b-dpo) a través de OpenRouter,
almacenando el historial de conversación en un archivo JSON local. Está diseñado para ser
usado desde regiones con restricciones (como Cuba), sin necesidad de tarjeta ni número de teléfono.

✅ Funcionalidades principales:
- Conexión a OpenRouter usando tu API key.
- Carga y guardado de historial en `mensaje_modelo.json`.
- Memoria persistente: el modelo "recuerda" la conversación entre ejecuciones.
- Límite inteligente del historial para evitar crecimiento infinito del archivo.
- Manejo de errores robusto (red, JSON, API).

📁 Estructura del archivo JSON:
[
  {"role": "system", "content": "..."},      → Instrucción inicial
  {"role": "user", "content": "..."},        → Tus preguntas
  {"role": "assistant", "content": "..."}    → Respuestas del modelo
]

🧩 Bloques lógicos del script:

1. 🔐 Conexión con OpenRouter
   - `openrouter_connect()`: crea las cabeceras con tu API key (desde .env).
   - Usa el modelo gratuito `qwen/qwen-turbo`.

2. 💬 Gestión del historial
   - `cargar_mensajes()`: lee el historial desde `mensaje_modelo.json`.
   - `agregar_mensaje_usuario()`: añade tu pregunta al historial.
   - El historial incluye contexto para mantener conversaciones coherentes.

3. 📡 Comunicación con la API
   - `crear_payload()`: prepara los datos para enviar a la API.
   - `hacer_solicitud_http_al_modelo()`: hace la solicitud POST y maneja errores de red.

4. 🧹 Limpieza inteligente del historial
   - Extrae el mensaje `system`.
   - Agrupa intercambios (user → assistant).
   - Mantiene solo los últimos N intercambios (por defecto 5).
   - Evita que el archivo crezca indefinidamente.
   - Funciones: `extraer_system_y_conversacion`, `agrupar_en_pares`, `limitar_historial_inteligente`, etc.

5. 💾 Actualización del historial
   - `actualizar_json_mensaje_qwen()`: 
        a) Agrega la respuesta del modelo.
        b) Limita el historial.
        c) Guarda en el archivo JSON.

⚡ Flujo de ejecución:
  1. Cargar historial
  2. Agregar nueva pregunta
  3. Enviar a Qwen vía OpenRouter
  4. Recibir y mostrar respuesta
  5. Agregar respuesta al historial
  6. Limitar historial (solo últimos intercambios)
  7. Guardar en disco

🔐 Configuración requerida:
  - Crea un archivo `.env` en la misma carpeta:
        OPENROUTER_API_KEY=tu_api_key_aqui

  - Asegúrate de tener instalado:
        pip install requests python-dotenv

📌 Notas:
  - Si estás en Cuba y no resuelve `openrouter.ai`, usa una VPN (ProtonVPN, Windscribe).
  - El archivo `mensaje_modelo.json` debe existir (puedes crear uno vacío o con un system prompt).
  - Puedes cambiar `max_intercambios` en `limitar_historial_inteligente` según necesites más o menos contexto.

💡 Próximos pasos (ideas):
  - Convertirlo en un chat interactivo con `while True` y `input()`.
  - Añadir resumen automático del historial si es muy largo.
  - Soporte para múltiples modelos (DeepSeek, Mistral, etc.).

Creado por: Abel
Fecha: Agosto 2025
"""

# Funciones de limpieza de contexto (Limpieza del JSON de Mensajes)

# Definimos un alias para claridad en anotaciones de tipo
Mensaje = Dict[str, Any]  # Ej: {"role": "user", "content": "..."}
Par = Dict[str, Mensaje | None]  # Ej: {"user": msg, "assistant": msg}
Historial = List[Mensaje]

def extraer_system_y_conversacion(mensajes: Historial) -> Tuple[Mensaje | None, Historial]:
    """
    Separa el mensaje system de los mensajes de conversación.
    Args:
        mensajes (Historial): Lista de mensajes que contiene el mensaje system y los mensajes de conversación
    Returns:
        Tuple[Mensaje | None, Historial]: Una tupla con el mensaje system (o None si no existe)
        y la lista de mensajes de conversación.
    """
    system_msg = None
    conversacion = []
    for msg in mensajes:
        if msg["role"] == "system":
            system_msg = msg
        elif msg["role"] in ["user", "assistant"]:
            conversacion.append(msg)
    return system_msg, conversacion


def agrupar_en_pares(conversacion: Historial) -> List[Par]:
    """
    Agrupa mensajes en pares: {user: ..., assistant: ...}
    Si un user no tiene assistant, se guarda igual.
    Args:
        conversacion (Historial): Lista de mensajes de conversación.
    Returns:
        List[Par]: Lista de pares de mensajes, donde cada par contiene un mensaje de usuario
    """
    pares = []
    i = 0
    while i < len(conversacion):
        user_msg = None
        assistant_msg = None

        # Buscar mensaje de usuario
        if conversacion[i]["role"] == "user":
            user_msg = conversacion[i]
            i += 1
        else:
            i += 1
            continue

        # Buscar siguiente mensaje de assistant
        if i < len(conversacion) and conversacion[i]["role"] == "assistant":
            assistant_msg = conversacion[i]
            i += 1

        pares.append({"user": user_msg, "assistant": assistant_msg})
    return pares


def mantener_ultimos_pares(pares: List[Par], max_intercambios: int) -> List[Par]:
    """
    Retorna los últimos N pares.
    Args:
        pares (List[Par]): Lista de pares de mensajes.
        max_intercambios (int): Número máximo de intercambios a mantener.
    Returns:
        List[Par]: Lista de los últimos N pares de mensajes.
    """
    return pares[-max_intercambios:]


def reconstruir_historial(system_msg: Mensaje | None, pares: List[Par]) -> Historial:
    """
    Reconstruye la lista de mensajes a partir de system + pares.
    Args:
        system_msg (Mensaje | None): Mensaje system, si existe.
        pares (List[Par]): Lista de pares de mensajes.
    Returns:
        Historial: Lista de mensajes reconstruida.
    """
    mensajes = []
    if system_msg:
        mensajes.append(system_msg)
    for par in pares:
        mensajes.append(par["user"])
        if par["assistant"]:
            mensajes.append(par["assistant"])
    return mensajes


def limitar_historial_inteligente(mensajes: Historial, max_intercambios: int = 5) -> Historial:
    """
    Limita el historial manteniendo el system y los últimos N intercambios.
    Args:
        mensajes (Historial): Lista de mensajes completa.
        max_intercambios (int): Número máximo de intercambios a mantener.
    Returns:
        Historial: Lista de mensajes limitada a system + últimos N pares.
    """
    system_msg, conversacion = extraer_system_y_conversacion(mensajes)
    pares = agrupar_en_pares(conversacion)
    pares_recientes = mantener_ultimos_pares(pares, max_intercambios)
    return reconstruir_historial(system_msg, pares_recientes)



# 2. Funciones de conexión y carga
# Usamos OpenRouter, no Qwen directamente
def openrouter_connect() -> tuple:
    """
    Crea una conexión con OpenRouter como intermediario para usar APIs de modelos de IA libres de costo.
    Carga la API key desde el entorno y verifica que no esté vacía.
    Retorna una tupla con la URL y las cabeceras necesarias para la solicitud.
    """
    # URL de la API de OpenRouter
    url = "https://openrouter.ai/api/v1/chat/completions"
    # Cargar la API key desde el entorno
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("API key de OpenRouter no encontrada en el entorno.")
    # Verificar que la API key no esté vacía
    if not api_key.strip():
        raise ValueError("API key de OpenRouter está vacía.")
    # Cabeceras
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    return url, headers


def cargar_mensajes(mensaje_json:str) -> list:
    """
    Carga los mensajes iniciales desde un archivo JSON.

    Args:
        mensaje_json (str): Nombre del json con el mensaje inicial para el modelo de IA

    Returns:
        list: Lista de mensajes cargados desde el archivo JSON.
    Si el archivo no existe, retorna una lista vacía.
    """
    try:
        with open(mensaje_json, "r", encoding="utf-8") as file:
            lista_messages = json.load(file)
            return lista_messages
    except FileNotFoundError:
        print(f"Archivo {mensaje_json} no encontrado. Retornando lista vacía.")
        return []


def agregar_mensaje_usuario(lista_messages:list, mensaje_usuario: str) -> None:
    """
    Método que agrega un mensaje del usuario al historial de mensajes.
    Args:
        mensaje_usuario (str): El mensaje del usuario a agregar.
    Modifica la lista de mensajes globalmente.
    No retorna nada.
    """
    try:
        lista_messages.append({"role": "user", "content": mensaje_usuario})
    except Exception as e:
        print(f"Error al agregar mensaje del usuario: {e}")
        raise


def crear_payload(lista_messages:list,modelo: str) -> dict:
    """
    Prepara los datos del modelo para la solicitud.
    Args:
        modelo (str): El nombre del modelo a usar.
    Returns:
        dict: Un diccionario con los datos del modelo.
    """
    try:
        if modelo == "qwen":
            modelo = "qwen/qwen-turbo"
        elif modelo == "mistral":
            modelo = "mistralai/mistral-7b-instruct"
        elif modelo == "mixtral":
            modelo = "nousresearch/nous-hermes-2-mixtral-8x7b-dpo"
        data = {
        "model": modelo,  # ✅ Modelo gratuito activo
        "messages": lista_messages,
        "temperature": 0.7
        }
        return data
    except Exception as e:
        print(f"Error al crear el payload: {e}")
        raise


def hacer_solicitud_http_al_modelo(url: str, headers: dict, data: dict) -> requests.Response:
    """Hace una solicitud POST al modelo de IA usando la URL, cabeceras y datos proporcionados.

    Args:
        url (str): La URL del modelo de IA.
        headers (dict): Cabeceras de la solicitud.
        data (dict): Payload de la solicitud.

    Returns:
        requests.Response: Respuesta a la solicitud POST a la URL de la IA

    Exceptions:
        requests.RequestException: Si ocurre un error al hacer la solicitud.
    """
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # ← Lanza excepción si no es 2xx
        return response  # ← Solo si fue exitosa
    except requests.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            print(f"Error {e.response.status_code}: {e.response.text}")
        else:
            print(f"Error de conexión: {e}")
        raise  # Re-lanza para que el llamador lo maneje


def actualizar_json_mensaje_qwen(lista_messages: list, response: requests.Response, mensaje_json: str) -> None:
    """
    Actualiza el archivo JSON con la respuesta del modelo.
    Si la solicitud es exitosa y la respuesta es JSON válido:
    1. Agrega la respuesta del modelo al historial.
    2. Limita el historial para evitar crecimiento indefinido (mantiene system + últimos intercambios).
    3. Guarda el historial limitado en el archivo.

    Args:
        lista_messages (list): Lista de mensajes que se actualizará con la respuesta del modelo.
        response (requests.Response): La respuesta de la API.
        mensaje_json (str): El nombre del archivo JSON a actualizar.

    Returns:
        None: No retorna nada. Modifica la lista y guarda en el archivo.

    Note:
        - Si la respuesta no es exitosa (código != 200), se imprime el error y no se guarda.
        - Si la respuesta no es JSON válido, se imprime el error y no se guarda.
        - No se lanzan excepciones; todos los errores se manejan internamente.
        - El historial se limita a los últimos 5 intercambios (ajustable en limitar_historial_inteligente). ← CAMBIO (actualizado en docstring)
    """
    if response.status_code != 200:
        print("Error:", response.status_code)
        print(response.text)
        return

    try:
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        print("Respuesta:")
        print(reply)

        # Agregar la respuesta del modelo al historial
        lista_messages.append({"role": "assistant", "content": reply})

        # ← CAMBIO: Limitar el historial ANTES de guardar
        lista_limitada = limitar_historial_inteligente(lista_messages, max_intercambios=5)

        # ← CAMBIO: Guardar el historial limitado, no el original
        with open(mensaje_json, "w", encoding="utf-8") as file:
            json.dump(lista_limitada, file, indent=2, ensure_ascii=False)

    except json.JSONDecodeError as e:
        print(f"Error al decodificar la respuesta JSON: {e}")
        print("Contenido recibido (no es JSON):")
        print(response.text)



# Implementaciones
ruta_actual = Path(".")
ruta_raiz = ruta_actual.parent
ruta_mensaje_modelo = ruta_raiz / "contexto/mensaje_modelo.json"
if __name__ == "__main__":
    lista_messages = cargar_mensajes(str(ruta_mensaje_modelo))
    agregar_mensaje_usuario(lista_messages, "Hola, ¿cómo te llamas?")
    data = crear_payload(lista_messages, "mistral")
    url, headers = openrouter_connect()
    response = hacer_solicitud_http_al_modelo(url, headers, data)
    actualizar_json_mensaje_qwen(lista_messages, response, str(ruta_mensaje_modelo))


