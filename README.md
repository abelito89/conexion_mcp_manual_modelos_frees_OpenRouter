¡Perfecto! Aquí tienes un **`README.md` profesional, claro y completo**, listo para tu proyecto MCP.

---

### ✅ `README.md` — Cliente MCP con Ejecución Manual de Herramientas


# 🧠 Cliente MCP con Ejecución Manual de Herramientas

Este proyecto implementa un cliente para el **Model Context Protocol (MCP)** que permite a un modelo de IA (como Mistral) interactuar con herramientas externas, incluso cuando **no soporta `tool_calls` nativos**.

Dado que modelos gratuitos como `mistralai/mistral-7b-instruct` en OpenRouter **no generan `tool_calls` reales**, este sistema **simula el flujo MCP** mediante **detección de intención en texto** y ejecución manual vía FastMCP.


## 🎯 Objetivo

- ✅ Permitir que un modelo use herramientas externas.
- ✅ Funcionar desde regiones con restricciones (como Cuba).
- ✅ No depender de modelos de pago (GPT, Gemini, etc.).
- ✅ Mantener un diseño modular, limpio y escalable.

---

## 🧩 Arquitectura

El sistema está dividido en módulos claros:

```
conexion_API_GitHub/
│
├── client.py                     # Orquestador principal
├── contexto/                     # Archivos de entrada/salida
│   ├── mensaje_modelo.json       # Historial y system prompt
│   └── contrato_tools.json       # Definición de herramientas
│
├── server.py                     # Servidor MCP con herramientas
│
└── src/
    ├── chat_modelo_local.py      # Conexión a OpenRouter y gestión de historial
    ├── mcp_manual.py             # Detección y ejecución manual de herramientas
    ├── contrato_y_payload.py     # Gestión del contrato y payload
    ├── procesamiento_respuesta.py# Extracción de respuestas
    └── historial_y_contexto.py   # Carga y guardado del historial
```

---

## 🛠️ Funcionalidad Clave

### 1. **Detección de intención**
- Usa `debe_usar_tool()` para detectar si el modelo quiere usar una herramienta.
- Basado en palabras clave, frases de acción y contexto.
- **Genérico**: funciona con cualquier herramienta.

### 2. **Ejecución manual de herramientas**
- `ejecutar_tool_manual()` llama a la herramienta vía FastMCP.
- Simula el comportamiento de un `tool_call` real.

### 3. **Simulación de `tool_call`**
- `agregar_al_historial_simulando_call_tool()` añade el resultado al historial en formato compatible.
- El modelo puede usar el resultado en su respuesta final.

### 4. **Gestión de historial**
- Carga y guarda el historial en `contexto/mensaje_modelo.json`.
- Límite inteligente para evitar crecimiento infinito.

---

## 🚀 Cómo usar

### 1. Clona el repositorio
```bash
git clone https://github.com/abelito89/conexion_mcp_manual_modelos_frees_OpenRouter.git
cd conexion_API_GitHub
```

### 2. Configura tu entorno
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

### 3. Instala dependencias
```bash
pip install requests python-dotenv fastmcp
```

### 4. Configura tu API key
Crea un archivo `.env`:
```env
OPENROUTER_API_KEY=tu_api_key_aqui
```

### 5. Ejecuta el servidor MCP
En una terminal:
```bash
python server.py
```

### 6. Ejecuta el cliente
En otra terminal:
```bash
python client.py
```

---

## 📂 Estructura de archivos clave

### `contexto/mensaje_modelo.json`
```json
[
  {
    "role": "system",
    "content": "Eres un asistente que puede usar herramientas externas. Si se te pide usar una herramienta, no expliques, solo úsala."
  },
  {
    "role": "user",
    "content": "Usa la herramienta 'hola_mundo_mcp' con el mensaje 'Hola desde Cuba'"
  }
]
```

### `contrato_tools.json`
```json
[
  {
    "type": "function",
    "function": {
      "name": "hola_mundo_mcp",
      "description": "Devuelve un mensaje y un timestamp",
      "parameters": {
        "type": "object",
        "properties": {
          "mensaje": { "type": "string" }
        },
        "required": ["mensaje"]
      }
    }
  }
]
```

---

## 🧪 Flujo de ejecución

1. El modelo recibe una solicitud con herramientas disponibles.
2. Responde con texto que indica intención de usar una herramienta.
3. El cliente detecta esta intención.
4. Se ejecuta la herramienta vía FastMCP (`server.py`).
5. El resultado se agrega al historial como si fuera un `tool_call`.
6. Se hace una segunda llamada al modelo con el resultado.
7. El modelo genera una respuesta final basada en el resultado.

---

## 📌 Notas importantes

- Este sistema **no depende de `tool_calls` nativos**, por lo que funciona con modelos gratuitos.
- La detección es por texto, no automática. Es un **MCP simulado**.
- Puedes añadir más herramientas modificando el contrato y el `server.py`.

---

## 🛡️ Licencia

Este proyecto es de código abierto y puede usarse libremente. No tiene licencia específica (public domain).

---

## 🙌 Créditos

Desarrollado por: **Abel**  
Fecha: Agosto 2025  