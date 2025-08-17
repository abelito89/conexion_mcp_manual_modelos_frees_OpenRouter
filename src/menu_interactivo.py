# src/menu_interactivo.py
"""
Módulo que gestiona el menú interactivo para seleccionar herramientas.
Permite al usuario elegir una herramienta y mantiene el programa activo hasta que decida salir.
"""

import asyncio
import os
from typing import Callable, Any
from logging_mcp import info, success, error, warning, debug, separator
from pathlib import Path
import json


ruta_actual = Path(".")
ruta_raiz = ruta_actual.parent
RUTA_CONTRATO = ruta_raiz / "contexto/contrato_tools.json"

def limpiar_pantalla() -> None:
    """Limpia la pantalla del terminal de forma portable (Windows, Linux, Mac).
    """
    os.system("cls" if os.name == "nt" else "clear")


def cerrar_programa() -> None:
    """
    Imprime un mensaje de despedida al cerrar el programa.
    """
    separator()
    info("\n👋 Gracias por usar el cliente MCP. ¡Hasta pronto!")


def cargar_herramientas_del_contrato() -> dict[int, str]:
    """Carga las herramientas disponibles desde contrato_tools.json.
    Devuelve un diccionario {número: nombre_herramienta}.

    Returns:
        dict[int, str]: Diccionario con las herramientas disponibles.
        Si no se puede cargar el contrato, retorna un diccionario con una herramienta por defecto.
    """
    try:
        with open(RUTA_CONTRATO, "r", encoding="utf-8") as f:
            contrato = json.load(f)
        return {i + 1: tool["function"]["name"] for i, tool in enumerate(contrato)}
    except Exception as e:
        from .logging_mcp import error
        error(f"No se pudo cargar el contrato de herramientas: {e}")
        return {1: "suma"}  # Fallback


def menu_interactivo(main_func: Callable[[str], Any]) -> None:
    """
    Muestra un menú interactivo para seleccionar herramientas.
    El programa se mantiene vivo hasta que el usuario elija salir (0).

    Args:
        main_func (Callable[[str], Any]): 
            Función principal asincrónica que ejecuta una herramienta dada su nombre.
            Se espera que reciba un str (nombre de herramienta) y devuelva cualquier tipo.
            Ejemplo: `main(herramienta: str) -> None`
    """
    #HERRAMIENTAS_DISPONIBLES = {
    #    1: "hola_mundo_mcp",
    #    2: "suma"
    #}
    HERRAMIENTAS_DISPONIBLES = cargar_herramientas_del_contrato()
    while True:
        limpiar_pantalla()
        print("\n" + "🔧" * 20)
        print("   MENÚ DE HERRAMIENTAS")
        print("🔧" * 20)
        for num, nombre in HERRAMIENTAS_DISPONIBLES.items():
            print(f"  {num}. {nombre}")
        print("  0. Salir")
        print("🔹" * 20)

        try:
            opcion = int(input("\n> Selecciona una opción: "))
            if opcion == 0:
                cerrar_programa()
                break
            elif opcion in HERRAMIENTAS_DISPONIBLES:
                info(f"🔄 Ejecutando herramienta: {HERRAMIENTAS_DISPONIBLES[opcion]}")
                asyncio.run(main_func(HERRAMIENTAS_DISPONIBLES[opcion]))
            else:
                error("❌ Opción no válida. Elige un número del menú.")
                input("   Presiona ENTER para continuar...")  # ← PAUSA AQUÍ
        except ValueError:
            error("❌ Por favor, ingresa un número válido.")
            input("   Presiona ENTER para continuar...")  # ← PAUSA AQUÍ
        except KeyboardInterrupt:
            print("")  # Nueva línea después de Ctrl+C
            cerrar_programa()
            break


