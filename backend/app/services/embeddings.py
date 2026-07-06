# app/services/embeddings.py
from app.core.config import settings


def get_embeddings():
    if settings.llm_provider == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(model=settings.ollama_embed_model, base_url=settings.ollama_base_url)
    else:
        raise NotImplementedError("Not implemented for other vendros than ollama")
    raise ValueError(f"Unknown provider: {settings.llm_provider}")