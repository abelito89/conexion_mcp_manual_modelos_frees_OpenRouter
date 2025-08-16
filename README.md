# 🧠 Cliente MCP con Ejecución Manual de Herramientas

Este sistema permite a un modelo de IA (como Mistral) interactuar con herramientas externas a través del **Model Context Protocol (MCP)**, incluso cuando el modelo **no soporta `tool_calls` nativos**.

Dado que modelos gratuitos como `mistralai/mistral-7b-instruct` en OpenRouter **no generan `tool_calls` reales**, este sistema **simula el flujo MCP** mediante:
- ✅ Detección de intención por texto.
- ✅ Ejecución manual vía FastMCP.
- ✅ Gestión dinámica del contexto.
- ✅ Soporte para múltiples herramientas.

El sistema es **modular, escalable y funcional en entornos con restricciones** (como Cuba), sin depender de modelos de pago.

---

## 🔄 Flujo del sistema

1. **Inicio**: El cliente (`client.py`) recibe el nombre de una herramienta (ej: `"suma"`).
2. **Contexto temporal**: Se crea un archivo temporal a partir de `contexto/mensaje_modelo.json`, que contiene un `system prompt` que obliga al modelo a repetir el nombre de la herramienta.
3. **Inyección de mensaje**: Se inyecta dinámicamente un mensaje como `"Herramienta 'suma'"` en el historial.
4. **Solicitud al modelo**: Se envía el historial al modelo vía OpenRouter.
5. **Detección de intención**: Si el modelo responde con `"Voy a usar la herramienta suma"`, se activa la ejecución.
6. **Ejecución de herramienta**: Se llama a `server.py` vía FastMCP usando `ejecutar_tool_manual`.
7. **Simulación de `tool_call`**: El resultado se agrega al historial como un mensaje de rol `tool`, usando `agregar_al_historial_simulando_call_tool`.
8. **Segunda consulta**: Se pregunta al modelo `"¿Qué resultado se obtuvo?"` para que use el resultado.
9. **Respuesta final**: El modelo genera una respuesta basada en el resultado.
10. **Limpieza**: El archivo temporal se elimina, dejando el sistema listo para la próxima ejecución.

---

## 🧩 Tecnologías clave

- **FastMCP**: Para definir y ejecutar herramientas en `server.py`.
- **Pydantic (`BaseModel`)**: Para estructurar y serializar los resultados de las herramientas (ej: `PingResponse`, `IntResponse`).
- **OpenRouter**: Como proveedor del modelo IA.
- **Módulos personalizados**: Divididos en `src/` para mantener el código limpio y escalable.

---

## 🛠️ Cómo agregar una nueva herramienta

Para que una nueva herramienta esté disponible para el modelo, debes seguir estos pasos:

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

### 4. **Ejecutar con el nombre correcto**
- En `client.py`, llama a `main("nombre_de_tu_herramienta")`.
- El sistema inyectará el mensaje, detectará la intención y ejecutará la herramienta.

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
    ├── mcp_manual.py             # Detección, ejecución y gestión de argumentos
    ├── contrato_y_payload.py     # Carga contrato y crea payload
    ├── chat_modelo_local.py      # Conexión a OpenRouter
    ├── procesamiento_respuesta.py# Extracción de respuestas
    └── historial_y_contexto.py   # Gestión de historial y contexto temporal
```

---

## 📌 Notas importantes

- ✅ El `system prompt` en `mensaje_modelo.json` obliga al modelo a repetir el nombre de la herramienta → esto permite la detección manual.
- ✅ No uses `tool_choice="required"`: muchos modelos gratuitos no lo soportan (causa `404`).
- ✅ Las herramientas deben devolver objetos basados en `BaseModel` para que sean serializables.
- ✅ El sistema es **genérico**: añadir una nueva herramienta solo requiere los 4 pasos anteriores.

---

## 🛡️ Licencia

Este proyecto es de código abierto y puede usarse libremente. No tiene licencia específica (public domain).

---

## 🙌 Créditos

Desarrollado por: **Abel Gómez Méndez**  
E-mail: **abelmetaltele@gmail.com**  
Móvil: **+5351368261**  
Fecha: Agosto 2025