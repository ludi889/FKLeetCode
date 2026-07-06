# app/services/embeddings.py
from app.core.config import settings

def get_embeddings():
    if settings.embeddings_provider == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(
            model=settings.embeddings_model, 
            base_url=settings.ollama_base_url
        )
        
    elif settings.embeddings_provider == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model=settings.embeddings_model, 
            google_api_key=settings.embeddings_api_key,
            output_dimensionality=768 
        )
        
    else:
        raise NotImplementedError(f"Not implemented for vendor: {settings.embeddings_provider}")