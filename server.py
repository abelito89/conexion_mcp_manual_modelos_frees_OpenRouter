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

@mcp.tool()
def hola_mundo_mcp(mensaje:str) -> PingResponse:
    """Devuelve un mensaje de respuesta para verificar la conexión."""
    return PingResponse(mensaje=mensaje, timestamp=datetime.now())

if __name__ == "__main__":
    # Arranca el servidor con la configuración por defecto de FastMCP
    mcp.run()
