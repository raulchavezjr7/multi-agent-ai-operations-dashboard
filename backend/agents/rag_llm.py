from typing import Any, ClassVar

import requests
from langchain_core.language_models import LLM

from backend.log_helper import log_agent_event


#  This is the base agent used for rag interpretation in rag_pipeline.py
class RagLLM(LLM):
    model: ClassVar[str] = "meta-llama-3.1-8b-instruct"

    @property
    def _llm_type(self) -> str:
        return "lmstudio"

    # This function transfers data to log_helper.py to log agent activity
    def log_agent(
        self,
        agent_role: str,
        label: str,
        request_type: str,
        message_overview: str,
        prompt_tokens: int,
        completion_tokens: int,
        prompt_desc: str,
        prompt: str,
    ):
        log_agent_event(
            agent_name="Rag Agent",
            agent_role=agent_role,
            label=label,
            request_type=request_type,
            message_overview=message_overview,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            details={prompt_desc: prompt[:200]},
        )

    # This functions call the model and awaits response rag interpretation
    def _call(self, prompt, stop=None, run_manager=None, **kwargs: Any):
        try:
            response = requests.post(
                "http://127.0.0.1:1234/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Use only the provided context to answer."
                                "Keep responses concise, structured, and under 300 tokens."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 400,
                    "stop": ["<|end|>", "<|endoftext|>", "<|assistant|>"],
                },
            )

            response.raise_for_status()
            result = response.json()

            self.log_agent(
                "Rag base agent",
                "Processed",
                "prompt",
                "Daily overview request",
                int(result["usage"]["prompt_tokens"]),
                0,
                "prompt_preview",
                prompt,
            )
            self.log_agent(
                "Rag base agent",
                "Processed",
                "response",
                "Rag agent response",
                0,
                int(result["usage"]["total_tokens"]),
                "response_preview",
                result["choices"][0]["message"]["content"],
            )
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            error_msg = f"Failed at LLM response: {str(e)}"
            self.log_agent(
                "Rag base agent",
                "ERROR",
                "error",
                "Failed rag agent response",
                0,
                0,
                "error details",
                error_msg,
            )
            return f"LLM error {error_msg}"
