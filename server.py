# server.py
# docstring del archivo
"""Servidor FastMCP para demostrar el uso de herramientas
y la interacción con un cliente CLI.
"""
from fastmcp import FastMCP
from pydantic import BaseModel
from datetime import datetime

mcp = FastMCP("DemoLocura FastMCP")

class PingResponse(BaseModel):
    mensaje: str
    timestamp: datetime
    detalle: str

class IntResponse(BaseModel):
    entero: str
    detalle: str

@mcp.tool()
def hola_mundo_mcp(mensaje:str) -> PingResponse:
    """Devuelve un mensaje de respuesta para verificar la conexión y la hora exacta del momento actual"""
    return PingResponse(mensaje=mensaje, timestamp=datetime.now(), detalle=f"Se envía el siguiente mensaje: {mensaje} a la hora: {datetime.now()}")

@mcp.tool()
def suma(numero1:int, numero2:int) -> IntResponse:
    """
    Suma dos números.

    Args:
        numero1 (int): Primer número a sumar.
        numero2 (int): Segundo número a sumar.

    Returns:
        int: La suma de los dos números.
    """
    entero = numero1 + numero2
    return IntResponse(entero=str(entero),
                       detalle=f"La suma de {numero1} y {numero2} es {entero}.")


if __name__ == "__main__":
    # Arranca el servidor con la configuración por defecto de FastMCP
    mcp.run()
