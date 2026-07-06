# app/services/llm.py
from app.core.config import settings


def get_chat_model():
    if settings.llm_provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=settings.ollama_chat_model, base_url=settings.ollama_base_url)
    else:
        raise NotImplementedError("Not implemented for other providers than ollama")