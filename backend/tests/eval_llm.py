# backend/tests/eval_llm.py
from deepeval.models import DeepEvalBaseLLM
from langchain_ollama import ChatOllama
from app.core.config import settings


class JudgeModel(DeepEvalBaseLLM):
    def __init__(self):
        if settings.eval_provider == "ollama":
            self.judge_model = ChatOllama(model=settings.eval_model, base_url=settings.ollama_base_url)
        elif settings.eval_provider == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.judge_model = ChatGoogleGenerativeAI(model=settings.eval_model, api_key=settings.eval_api_key)
        else:
            raise NotImplementedError("Not implemented for other vendors than ollama")

    def load_model(self):
        return self.judge_model

    def _extract_text(self, content) -> str:
        """LangChain's AIMessage.content is str for most providers, but a list of
        content-part dicts for ChatGoogleGenerativeAI. Normalize to a plain string."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        return str(content)

    def generate(self, prompt: str) -> str:
        """Synchronous generation (used by some DeepEval features)"""
        judge_model = self.load_model()
        return self._extract_text(judge_model.invoke(prompt).content)

    async def a_generate(self, prompt: str) -> str:
        """Asynchronous generation (used by DeepEval for fast parallel evals)"""
        judge_model = self.load_model()
        response = await judge_model.ainvoke(prompt)
        return self._extract_text(response.content)

    def get_model_name(self):
        return f"{settings.eval_provider} - {self.judge_model.model}"