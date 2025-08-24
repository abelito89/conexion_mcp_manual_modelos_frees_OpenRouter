
# 🧠 Cliente MCP con Ejecución Manual de Herramientas

### ✅ `README.md` — Cliente MCP con Ejecución Manual de Herramientas


# 🧠 Cliente MCP con Ejecución Manual de Herramientas

Este sistema permite a un modelo de IA (como Mistral) interactuar con herramientas externas a través del **Model Context Protocol (MCP)**, incluso cuando el modelo **no soporta `tool_calls` nativos**.

Dado que modelos gratuitos como `mistralai/mistral-7b-instruct` en OpenRouter **no generan `tool_calls` reales**, este sistema **simula el flujo MCP** mediante:
- ✅ **Detección de intención semántica**: Utiliza embeddings para comprender la intención del modelo de usar una herramienta, en lugar de depender de frases exactas.
- ✅ **Ejecución manual vía FastMCP**: Llama a las herramientas definidas en `server.py`.
- ✅ **Gestión dinámica del contexto**: Adapta el `system_prompt` y el historial de mensajes para guiar al modelo en cada paso.
- ✅ **Soporte para múltiples herramientas**: El sistema es fácilmente extensible.

El sistema es **modular, interactivo, escalable y funcional en entornos con restricciones** (como Cuba), sin depender de modelos de pago.

---

## 🔄 Flujo del sistema

1. **Inicio y Selección**: El usuario ejecuta `client.py` y selecciona una herramienta del menú interactivo.
2. **Inyección de Mensaje**: Se inyecta un mensaje en el historial para indicarle al modelo qué herramienta se ha seleccionado.
3. **Detección de Intención**: Se envía el historial al modelo. El cliente utiliza un **detector semántico** (`debe_usar_tool_semantico`) para analizar la respuesta del modelo y determinar si tiene la intención de usar la herramienta.
4. **Solicitud de Argumentos**: Si se detecta la intención, el sistema solicita al usuario los argumentos necesarios para la herramienta (ej: los números para la `suma`).
5. **Ejecución de Herramienta**: Se ejecuta la herramienta correspondiente en `server.py` a través de FastMCP.
6. **Simulación de `tool_call`**: El resultado de la herramienta se agrega al historial de conversación.
7. **Generación de Respuesta Final**: Se cambia dinámicamente el `system_prompt` para instruir al modelo que presente el resultado de una manera amigable y conversacional. Se realiza una última llamada al modelo.
8. **Visualización y Limpieza**: Se muestra la respuesta final al usuario, se guarda el historial y se limpia el contexto temporal para la siguiente ejecución.

---

## 🧩 Tecnologías clave

- **Sentence Transformers**: Para la detección de intención semántica.
- **FastMCP**: Para definir y ejecutar herramientas en `server.py`.
- **Pydantic (`BaseModel`)**: Para estructurar y serializar los resultados de las herramientas (ej: `PingResponse`, `IntResponse`).
- **OpenRouter**: Como proveedor del modelo IA.
- **Módulos personalizados**: Divididos en `src/` para mantener el código limpio, escalable y bien organizado.
- **Sistema de logging**: Basado en el módulo estándar `logging`, con colores y niveles (`info`, `error`, `success`, etc.).

---

## 🛠️ Cómo agregar una nueva herramienta

Para que una nueva herramienta esté disponible para el modelo, sigue estos pasos:

### 1. **Crear la herramienta en `server.py`**
- Define una función decorada con `@mcp.tool()`.
- Usa `BaseModel` (de Pydantic) para estructurar la respuesta.
- Asegúrate de que los parámetros coincidan con lo que necesitas.

### 2. **Registrarla en `contrato_tools.json`**
- Añade la definición de la herramienta en formato JSON.
- Incluye nombre, descripción, parámetros y tipos.
- Este archivo es leído por el cliente para incluir la herramienta en el `payload`.

### 3. **Gestionar argumentos en `src/mcp_manual.py`**
- Modifica la función `extraer_argumentos_necesarios_herramienta`.
- Añade una condición para tu herramienta que devuelva los argumentos correctos según el contexto.

### 4. **Añadir Frases de Ejemplo (Opcional pero Recomendado)**
- En `src/deteccion_intencion/base_conocimiento.py`, añade frases de ejemplo para tu nueva herramienta. Esto mejorará la precisión de la detección semántica.

### 5. **Agregarla al menú en `src/menu_interactivo.py`**
- Añade la herramienta al diccionario que se carga desde `contrato_tools.json`. El menú se genera dinámicamente.

---

## 📂 Estructura del proyecto

```
proyecto/
│
├── client.py                     # Orquestador principal
├── server.py                     # Definición de herramientas (FastMCP)
├── contrato_tools.json           # Contrato de herramientas (lista de funciones)
├── contexto/
│   └── mensaje_modelo.json       # Plantilla de contexto (system prompt)
│
└── src/
    ├── chat_modelo_local.py      # Conexión a OpenRouter y gestión de historial
    ├── contrato_y_payload.py     # Carga de contrato y creación de payload
    ├── historial_y_contexto.py   # Gestión de historial y contexto temporal
    ├── logging_mcp.py            # Sistema de logging con niveles y colores
    ├── mcp_manual.py             # Detección, ejecución y gestión de argumentos
    ├── menu_interactivo.py       # Menú interactivo con pausas y limpieza
    ├── procesamiento_respuesta.py# Extracción de respuestas del modelo
    └── deteccion_intencion/
        ├── base_conocimiento.py  # Frases de ejemplo para la detección semántica
        ├── detector.py           # Lógica de detección de intención semántica
        ├── embeddings.py         # Creación de embeddings con Sentence Transformers
        └── utils.py              # Funciones de utilidad (ej: similitud de coseno)
```

---

## 📌 Notas importantes

- ✅ El `system prompt` en `mensaje_modelo.json` obliga al modelo a repetir el nombre de la herramienta → esto permite la detección manual.
- ✅ No uses `tool_choice="required"`: muchos modelos gratuitos no lo soportan (causa `404`).
- ✅ Las herramientas deben devolver objetos basados en `BaseModel` para que sean serializables.
- ✅ El sistema es **interactivo y persistente**: el menú no se cierra hasta que el usuario elige salir.
- ✅ El **sistema de logging** (`logging_mcp.py`) reemplaza todos los `print()` sueltos, mejorando la depuración y consistencia.
- ✅ El menú se limpia al inicio de cada ciclo para mejorar la legibilidad.
- ✅ Todas las salidas de error o éxito se pausan para que el usuario pueda leerlas.

---

## � Instalación y Configuración

1. **Clonar el repositorio**
```bash
git clone https://github.com/abelito89/conexion_mcp_manual_modelos_frees_OpenRouter.git
cd conexion_mcp_manual_modelos_frees_OpenRouter
```

2. **Crear y activar entorno virtual**
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Crear archivo .env
echo "OPENROUTER_API_KEY=tu_api_key_aqui" > .env
```

## 🧪 Pruebas

1. **Iniciar el servidor**
```bash
python server.py
```

2. **En otra terminal, ejecutar el cliente**
```bash
python client.py
```

3. **Probar herramienta básica**
   - Seleccionar opción 1 (hola_mundo_mcp)
   - Verificar la respuesta del modelo

## 📊 Ejemplos de Uso

### Ejemplo 1: Suma de números
```python
# Seleccionar opción 2 (suma)
# El modelo ejecutará la suma y mostrará el resultado
# Ejemplo de respuesta: "La suma de 5 y 3 es 8"
```

### Ejemplo 2: Hola Mundo personalizado
```python
# Seleccionar opción 1 (hola_mundo_mcp)
# Si mencionas "cuba" en el mensaje, responderá "Hola desde Cuba"
```

## 🛡️ Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙌 Créditos y Contacto

Desarrollado por: **Abel Gómez Méndez**  
E-mail: **abelmetaltele@gmail.com**  
Móvil: **+5351368261**  
Fecha: Agosto 2025

## 🤝 Contribuciones

## 🛡️ Licencia

Este proyecto es de código abierto y puede usarse libremente. No tiene licencia específica (public domain).

---

## 🙌 Créditos

Desarrollado por: **Abel Gómez Méndez**  
E-mail: **abelmetaltele@gmail.com**  
Móvil: **+5351368261**  
Fecha: Agosto 2025