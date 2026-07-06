# app/services/llm.py
from app.core.config import settings


def get_chat_model():
    if settings.llm_provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=settings.llm_model, base_url=settings.ollama_base_url)
    elif settings.llm_provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=settings.llm_model, api_key=settings.llm_api_key)
    else:
        raise NotImplementedError("Not implemented for other vendors than ollama")