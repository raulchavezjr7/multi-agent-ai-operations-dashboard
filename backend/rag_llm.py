from typing import Any, ClassVar

import requests
from langchain_core.language_models import LLM


class RagLLM(LLM):
    model: ClassVar[str] = "meta-llama-3.1-8b-instruct"

    @property
    def _llm_type(self) -> str:
        return "lmstudio"

    def _call(self, prompt, stop=None, run_manager=None, **kwargs: Any):
        response = requests.post(
            "http://127.0.0.1:1234/v1/chat/completions",
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Use only the provided context to answer.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
                "max_tokens": 400,
            },
        )
        return response.json()["choices"][0]["message"]["content"]
