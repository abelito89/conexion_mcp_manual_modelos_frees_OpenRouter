🚀 Chat con Qwen usando OpenRouter (sin OpenAI)

Este script permite interactuar con el modelo Qwen (qwen/qwen-turbo) a través de OpenRouter,
almacenando el historial de conversación en un archivo JSON local. Está diseñado para ser
usado desde regiones con restricciones (como Cuba), sin necesidad de tarjeta ni número de teléfono.

✅ Funcionalidades principales:
- Conexión a OpenRouter usando tu API key.
- Carga y guardado de historial en `mensaje_qwen.json`.
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
   - `cargar_mensajes()`: lee el historial desde `mensaje_qwen.json`.
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
  - El archivo `mensaje_qwen.json` debe existir (puedes crear uno vacío o con un system prompt).
  - Puedes cambiar `max_intercambios` en `limitar_historial_inteligente` según necesites más o menos contexto.

💡 Próximos pasos (ideas):
  - Convertirlo en un chat interactivo con `while True` y `input()`.
  - Añadir resumen automático del historial si es muy largo.
  - Soporte para múltiples modelos (DeepSeek, Mistral, etc.).

Creado por: Abel
Fecha: Agosto 2025