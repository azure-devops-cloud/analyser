from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class ModelProviderConfig:
    provider: str
    model: str
    priority: int = 0


class ModelProviderRegistry:
    """Simple registry for selecting a free/open-source inference provider."""

    def __init__(self, preferences: Optional[List[str]] = None):
        self.preferences = preferences or [
            "ollama",
            "huggingface",
            "github-models",
            "transformers",
        ]

    def select_best_free_model(self) -> ModelProviderConfig:
        registry: Dict[str, ModelProviderConfig] = {
            "ollama": ModelProviderConfig(provider="ollama", model="llama3.2", priority=100),
            "huggingface": ModelProviderConfig(provider="huggingface", model="sentence-transformers/all-MiniLM-L6-v2", priority=90),
            "github-models": ModelProviderConfig(provider="github-models", model="gpt-4o-mini", priority=70),
            "transformers": ModelProviderConfig(provider="transformers", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", priority=60),
        }

        for provider in self.preferences:
            candidate = registry.get(provider)
            if candidate is not None:
                return candidate

        return registry["transformers"]
