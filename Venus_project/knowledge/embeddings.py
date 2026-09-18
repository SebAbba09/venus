import hashlib
from functools import lru_cache
from typing import Protocol, Sequence, runtime_checkable

from django.conf import settings


@runtime_checkable
class EmbeddingProvider(Protocol):
    provider_name: str
    model_name: str | None
    dimension: int

    def embed(self, text: str) -> list[float]:
        ...

    def embed_many(self, texts: Sequence[str]) -> list[list[float]]:
        ...


class StubEmbeddingProvider:
    """Deterministic offline provider intended for tests and local development."""

    provider_name = 'stub'
    model_name = None

    def __init__(self, dimension: int = 8):
        if dimension <= 0:
            raise ValueError('dimension must be greater than zero')
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        if not text:
            return [0.0] * self.dimension

        digest = hashlib.sha256(text.encode('utf-8')).digest()
        return [
            (digest[index % len(digest)] / 255.0) * 2.0 - 1.0
            for index in range(self.dimension)
        ]

    def embed_many(self, texts: Sequence[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    provider = getattr(settings, 'M2_EMBEDDING_PROVIDER', 'stub').lower()
    if provider != 'stub':
        raise ValueError(f'Unsupported embedding provider: {provider}')

    dimension = getattr(settings, 'M2_EMBEDDING_DIMENSION', 8)
    return StubEmbeddingProvider(dimension=dimension)


def reset_embedding_provider_cache():
    get_embedding_provider.cache_clear()
