from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from django.conf import settings


@dataclass
class GeneratedResponse:
    text: str
    model_name: str
    backend: str | None = None
    sources: list[str] | None = None
    metadata: dict[str, Any] | None = None


class TextGenerator:
    """Abstract contract for the M2 generation layer.

    The generator may later receive conversation history, RAG context, and metadata,
    but the public contract stays stable and model-agnostic.
    """

    backend_name = "base"

    def generate(self, messages=None, context=None, **kwargs) -> GeneratedResponse:
        raise NotImplementedError


class StubGenerator(TextGenerator):
    backend_name = "stub"

    def generate(self, messages=None, context=None, **kwargs) -> GeneratedResponse:
        text = "Réponse de démonstration M2."
        if messages:
            last_user_message = next(
                (m["content"] for m in reversed(messages) if m.get("role") == "user"),
                "",
            )
            if last_user_message:
                text = f"Réponse M2 pour : {last_user_message}"
        return GeneratedResponse(
            text=text,
            model_name="stub-generator",
            backend=self.backend_name,
            sources=[],
            metadata={"messages_count": len(messages or []), "context": bool(context)},
        )


class TransformersGenerator(TextGenerator):
    backend_name = "transformers"

    def __init__(self, model_name=None, model_path=None):
        self.model_name = (model_name if model_name is not None else settings.M2_MODEL_NAME) or ""
        self.model_path = model_path if model_path is not None else settings.M2_MODEL_PATH
        self._tokenizer = None
        self._model = None

    def _load(self):
        if not self.model_name:
            raise ValueError("M2_MODEL_NAME must be configured before using the transformers backend.")

        from transformers import AutoModelForCausalLM, AutoTokenizer

        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self._model = AutoModelForCausalLM.from_pretrained(self.model_name)

    def generate(self, messages=None, context=None, **kwargs) -> GeneratedResponse:
        if not messages:
            prompt = context or "Bonjour"
        else:
            prompt = "\n".join(
                f"{m.get('role', 'user')}: {m.get('content', '')}"
                for m in messages if isinstance(m, dict)
            )
            if not prompt:
                prompt = context or "Bonjour"

        if self._model is None or self._tokenizer is None:
            self._load()

        import torch

        inputs = self._tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            output = self._model.generate(**inputs, max_new_tokens=150)
        text = self._tokenizer.decode(output[0], skip_special_tokens=True).strip()
        return GeneratedResponse(
            text=text,
            model_name=self.model_name,
            backend=self.backend_name,
            sources=[],
            metadata={"messages_count": len(messages or []), "context": bool(context)},
        )


@lru_cache(maxsize=1)
def get_generator():
    backend = getattr(settings, 'M2_GENERATOR_BACKEND', 'stub').lower()
    if backend == 'transformers':
        return TransformersGenerator()
    return StubGenerator()


def reset_generator_cache():
    get_generator.cache_clear()
