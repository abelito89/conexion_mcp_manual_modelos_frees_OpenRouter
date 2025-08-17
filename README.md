
### ✅ `README.md` — Cliente MCP con Ejecución Manual de Herramientas


# 🧠 Cliente MCP con Ejecución Manual de Herramientas

Este sistema permite a un modelo de IA (como Mistral) interactuar con herramientas externas a través del **Model Context Protocol (MCP)**, incluso cuando el modelo **no soporta `tool_calls` nativos**.

Dado que modelos gratuitos como `mistralai/mistral-7b-instruct` en OpenRouter **no generan `tool_calls` reales**, este sistema **simula el flujo MCP** mediante:
- ✅ Detección de intención por nombre de herramienta.
- ✅ Ejecución manual vía FastMCP.
- ✅ Gestión dinámica del contexto.
- ✅ Soporte para múltiples herramientas.

El sistema es **modular, interactivo, escalable y funcional en entornos con restricciones** (como Cuba), sin depender de modelos de pago.

---

## 🔄 Flujo del sistema

1. **Inicio**: El usuario inicia el programa y ve un menú interactivo.
2. **Selección**: Elige una herramienta del menú (ej: `1` para `suma`).
3. **Contexto temporal**: Se crea un archivo temporal a partir de `contexto/mensaje_modelo.json`, que contiene un `system prompt` que obliga al modelo a repetir el nombre de la herramienta.
4. **Inyección de mensaje**: Se inyecta dinámicamente un mensaje como `"Herramienta 'suma'"` en el historial.
5. **Solicitud al modelo**: Se envía el historial al modelo vía OpenRouter.
6. **Detección de intención**: Si el modelo responde con `"Voy a usar la herramienta suma"`, se activa la ejecución.
7. **Ejecución de herramienta**: Se llama a `server.py` vía FastMCP usando `ejecutar_tool_manual`.
8. **Simulación de `tool_call`**: El resultado se agrega al historial como un mensaje de rol `tool`, usando `agregar_al_historial_simulando_call_tool`.
9. **Segunda consulta**: Se pregunta al modelo `"¿Qué resultado se obtuvo?"` para que use el resultado.
10. **Respuesta final**: El modelo genera una respuesta basada en el resultado.
11. **Pausa para lectura**: El sistema espera a que el usuario presione `ENTER` antes de continuar.
12. **Limpieza**: El archivo temporal se elimina, y el menú vuelve a mostrarse.
13. **Persistencia**: El programa permanece activo hasta que el usuario elige salir (opción `0`).

---

## 🧩 Tecnologías clave

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

### 4. **Agregarla al menú en `src/menu_interactivo.py`**
- Añade la herramienta al diccionario `HERRAMIENTAS_DISPONIBLES`.
- Ejemplo: `3: "mi_nueva_herramienta"`.

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
    ├── historial_y_contexto.py   # Gestión de historial y contexto temporal
    ├── menu_interactivo.py       # Menú interactivo con pausas y limpieza
    └── logging_mcp.py            # Sistema de logging con niveles y colores
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

## 🛡️ Licencia

Este proyecto es de código abierto y puede usarse libremente. No tiene licencia específica (public domain).

---

## 🙌 Créditos

Desarrollado por: **Abel Gómez Méndez**  
E-mail: **abelmetaltele@gmail.com**  
Móvil: **+5351368261**  
Fecha: Agosto 2025