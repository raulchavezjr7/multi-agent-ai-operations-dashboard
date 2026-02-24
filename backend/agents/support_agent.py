from .base_agent import BaseAgent
import json


class SupportAgent(BaseAgent):
    def __init__(self, model="meta-llama-3.1-8b-instruct"):
        super().__init__(
            name="Support Agent",
            api_endpoint="http://127.0.0.1:8000/support/summary",
            model=model,
        )

    def build_prompt(self, data: dict):
        return (
            "You are the Support Agent for a operations dashboard.\n"
            "Analyze the following accounting summary data.\n"
            "Focus only on insights that are genuinely meaningful. "
            "Base your observations on what the data clearly suggests, and avoid speculation. "
            "Prioritize clarity and usefulness over completeness.\n\n"
            f"DATA:\n{json.dumps(data, indent=2)}"
        )
