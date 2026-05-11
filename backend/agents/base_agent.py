import json

import requests

from backend.log_helper import log_agent_event


# This is a Base Agent class that all domain agents inherit from. Supervisor and Rag agents do not inherit from this class.
class BaseAgent:
    def __init__(
        self, name: str, api_endpoint: str, model: str = "phi-3.1-mini-4k-instruct"
    ):
        self.name = name
        self.api_endpoint = api_endpoint
        self.model = model

    # This functions gets the overview data from the SQL ai_ops_database database
    def fetch_data(self):
        try:
            response = requests.get(self.api_endpoint)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            return {"error": f"Failed to fetch data: {e}"}

    # This functions build the overview prompt
    def build_prompt(self, data: dict):
        return (
            f"You are the {self.name}. Analyze the following JSON data and "
            f"provide insights, trends, anomalies, and recommendations.\n\n"
            f"DATA:\n{json.dumps(data, indent=2)}"
        )

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
            agent_name=self.name,
            agent_role=agent_role,
            label=label,
            request_type=request_type,
            message_overview=message_overview,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            details={prompt_desc: prompt[:200]},
        )

    # This function calls LLM model and awaits response
    def call_llm(self, prompt: str):
        try:
            response = requests.post(
                "http://127.0.0.1:1234/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                f"You are the {self.name}."
                                "Keep responses concise, structured, and under 300 tokens."
                                "Avoid filler, avoid repeating the prompt, and keep responses concise."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.4,
                    "max_tokens": 500,
                    "stop": ["<|end|>", "<|endoftext|>", "<|assistant|>"],
                },
                timeout=240,
            )
            response.raise_for_status()
            result = response.json()

            self.log_agent(
                "database overview",
                "Processed",
                "prompt",
                "Daily overview request",
                int(result["usage"]["prompt_tokens"]),
                0,
                "prompt_preview",
                prompt,
            )
            self.log_agent(
                "database overview",
                "Processed",
                "response",
                "Daily overview response",
                0,
                int(result["usage"]["total_tokens"]),
                "response_preview",
                result["choices"][0]["message"]["content"],
            )
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            error_msg = f"Failed at LLM response: {str(e)}"
            self.log_agent(
                "database overview",
                "ERROR",
                "error",
                "Failed daily response",
                0,
                0,
                "error details",
                error_msg,
            )
            return f"LLM error {error_msg}"

    # This function runs the overview process
    def run(self):
        data = self.fetch_data()
        prompt = self.build_prompt(data)
        insight = self.call_llm(prompt)
        return insight.strip()
