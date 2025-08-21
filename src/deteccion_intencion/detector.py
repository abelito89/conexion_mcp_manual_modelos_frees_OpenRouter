from .base_conocimiento import FRASES_POR_HERRAMIENTA
from .embeddings import texto_a_embedding
from .utils import similitud_coseno

# Cache de embeddings de frases (se calculan al inicio)
CACHE_FRASES = {}

def _precalcular_embeddings() -> None:
    """Precalcula embeddings para todas las frases de ejemplo."""
    global CACHE_FRASES
    for herramienta, frases in FRASES_POR_HERRAMIENTA.items():
        CACHE_FRASES[herramienta] = [texto_a_embedding(frase) for frase in frases]

# Precalcula al cargar el módulo
_precalcular_embeddings()

def debe_usar_tool_semantico(texto: str, nombre_tool: str, umbral: float = 0.75) -> bool:
    """
    Detecta si el texto tiene intención de usar una herramienta,
    usando similitud semántica con frases de ejemplo.
    
    Args:
        texto (str): Texto del modelo a analizar.
        nombre_tool (str): Nombre de la herramienta.
        umbral (float): Umbral de similitud (0.0 a 1.0). Default: 0.75.
    
    Returns:
        bool: True si hay intención de usar la herramienta.
    """
    if nombre_tool not in CACHE_FRASES:
        return False

    texto_norm = texto.strip()
    if not texto_norm:
        return False

    vector_input = texto_a_embedding(texto_norm)

    for vector_frase in CACHE_FRASES[nombre_tool]:
        sim = similitud_coseno(vector_input, vector_frase)
        if sim >= umbral:
            return True
    return False