import os
import numpy as np
from sentence_transformers import SentenceTransformer


_MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
_model = SentenceTransformer(_MODEL_NAME)

def embed_text(text: str) -> list[float]:
    if not text:
        return []
    v = _model.encode([text], normalize_embeddings=True)[0]
    return v.astype(float).tolist()

def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    va, vb = np.array(a), np.array(b)
    return float(np.clip(va @ vb, -1.0, 1.0))
