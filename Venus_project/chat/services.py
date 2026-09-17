from dataclasses import dataclass
from functools import lru_cache

from django.conf import settings


@dataclass
class GeneratedResponse:
    text: str
    model_name: str


class TextGenerator:
    """Small interface that keeps generation replaceable by the future RAG layer."""

    def generate(self, prompt: str) -> GeneratedResponse:
        raise NotImplementedError


class TransformersGenerator(TextGenerator):
    def __init__(self, model_name=None, model_path=None):
        self.model_name = model_name or settings.M2_MODEL_NAME
        self.model_path = model_path or settings.M2_MODEL_PATH
        self._tokenizer = None
        self._model = None

    def _load(self):
        from transformers import BlenderbotForConditionalGeneration, BlenderbotTokenizer

        tokenizer_source = self.model_name
        model_source = self.model_path or self.model_name
        self._tokenizer = BlenderbotTokenizer.from_pretrained(tokenizer_source)
        self._model = BlenderbotForConditionalGeneration.from_pretrained(model_source)

    def generate(self, prompt: str) -> GeneratedResponse:
        if self._model is None or self._tokenizer is None:
            self._load()

        import torch

        inputs = self._tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            output = self._model.generate(**inputs, max_new_tokens=150)
        text = self._tokenizer.decode(output[0], skip_special_tokens=True).strip()
        return GeneratedResponse(text=text, model_name=self.model_name)


@lru_cache(maxsize=1)
def get_generator():
    return TransformersGenerator()
