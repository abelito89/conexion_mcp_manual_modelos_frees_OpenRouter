from sentence_transformers import SentenceTransformer
import numpy as np

# Modelo ligero y rápido, ideal para embeddings semánticos
MODEL_NAME = "all-MiniLM-L6-v2"
_model = None  # Singleton para no cargar el modelo múltiples veces

def obtener_modelo() -> SentenceTransformer:
    """Carga o devuelve el modelo de embeddings (singleton).

    Returns:
        SentenceTransformer: Modelo de embeddings.
    """
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def texto_a_embedding(texto: str) -> np.ndarray:
    """Convierte un texto en su embedding semántico.

    Args:
        texto (str): Texto a convertir.

    Returns:
        np.ndarray: Embedding semántico del texto.
    """
    modelo = obtener_modelo()
    return modelo.encode(texto, convert_to_numpy=True)