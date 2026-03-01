import requests
import json


class BaseAgent:
    def __init__(
        self, name: str, api_endpoint: str, model: str = "phi-3.1-mini-4k-instruct"
    ):
        self.name = name
        self.api_endpoint = api_endpoint
        self.model = model

    def fetch_data(self):
        try:
            response = requests.get(self.api_endpoint)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            return {"error": f"Failed to fetch data: {e}"}

    def build_prompt(self, data: dict):
        return (
            f"You are the {self.name}. Analyze the following JSON data and "
            f"provide insights, trends, anomalies, and recommendations.\n\n"
            f"DATA:\n{json.dumps(data, indent=2)}"
        )

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
                    "max_tokens": 300,
                },
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"LLM error {e}"

    def run(self):
        data = self.fetch_data()
        prompt = self.build_prompt(data)
        insight = self.call_llm(prompt)
        return insight.strip()
