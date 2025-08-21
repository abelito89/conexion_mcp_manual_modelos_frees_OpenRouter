import numpy as np

def similitud_coseno(a: np.ndarray, b: np.ndarray) -> float:
    """Calcula similitud del coseno entre dos vectores.

    Args:
        a (np.ndarray): vector a
        b (np.ndarray): vector b

    Returns:
        float: similitud del coseno entre a y b
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def normalizar_texto(texto: str) -> str:
    """Normaliza texto para comparación.

    Args:
        texto (str): texto a normalizar

    Returns:
        str: texto normalizado
    """
    return texto.lower().strip()