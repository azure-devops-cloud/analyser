"""Provider-neutral model configuration with free-first defaults."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class ModelProviderConfig:
    provider: str
    model: str
    temperature: float = 0.0
    max_tokens: int = 2048
    timeout_seconds: float = 30.0
    priority: int = 0


class ModelProviderRegistry:
    """Resolve a model without coupling agents to a specific provider.

    The baseline intentionally defaults to local/open-weight inference. Remote
    providers can be configured later through environment variables without
    changing agent code.
    """

    def __init__(self, preferences: Optional[list[str]] = None):
        configured = os.getenv("MODEL_PROVIDER", "").strip().lower()
        self.preferences = preferences or ([configured] if configured else ["ollama", "transformers"])

    @staticmethod
    def _env_float(name: str, default: float) -> float:
        try:
            return float(os.getenv(name, str(default)))
        except ValueError:
            return default

    @staticmethod
    def _env_int(name: str, default: int) -> int:
        try:
            return int(os.getenv(name, str(default)))
        except ValueError:
            return default

    def _build(self, provider: str, model: str, priority: int) -> ModelProviderConfig:
        return ModelProviderConfig(
            provider=provider,
            model=model,
            temperature=self._env_float("MODEL_TEMPERATURE", 0.0),
            max_tokens=self._env_int("MODEL_MAX_TOKENS", 2048),
            timeout_seconds=self._env_float("MODEL_TIMEOUT", 30.0),
            priority=priority,
        )

    def select_best_free_model(self) -> ModelProviderConfig:
        registry = {
            "ollama": self._build("ollama", os.getenv("MODEL_NAME", "qwen3:4b"), 100),
            "transformers": self._build(
                "transformers",
                os.getenv("MODEL_NAME", "Qwen/Qwen3-4B-Instruct"),
                90,
            ),
        }

        for provider in self.preferences:
            candidate = registry.get(provider)
            if candidate is not None:
                return candidate

        return registry["transformers"]
