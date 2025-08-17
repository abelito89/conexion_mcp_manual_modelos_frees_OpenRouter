# src/menu_interactivo.py
"""
Módulo que gestiona el menú interactivo para seleccionar herramientas.
Permite al usuario elegir una herramienta y mantiene el programa activo hasta que decida salir.
"""

import asyncio
import os
from typing import Callable, Any


def limpiar_pantalla() -> None:
    """Limpia la pantalla del terminal de forma portable (Windows, Linux, Mac).
    """
    os.system("cls" if os.name == "nt" else "clear")


def cerrar_programa() -> None:
    """
    Imprime un mensaje de despedida al cerrar el programa.
    """
    print("\n👋 Gracias por usar el cliente MCP. ¡Hasta pronto!")


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
    HERRAMIENTAS_DISPONIBLES = {
        1: "hola_mundo_mcp",
        2: "suma"
    }

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
                asyncio.run(main_func(HERRAMIENTAS_DISPONIBLES[opcion]))
            else:
                print("❌ Opción no válida. Elige un número del menú.")
        except ValueError:
            print("❌ Por favor, ingresa un número válido.")
        except KeyboardInterrupt:
            print("")  # Nueva línea después de Ctrl+C
            cerrar_programa()
            break