from .base_agent import BaseAgent
import json


class OperationsAgent(BaseAgent):
    def __init__(self, model="phi-3.1-mini-4k-instruct"):
        super().__init__(
            name="Support Agent",
            api_endpoint="http://127.0.0.1:8000/operations/summary",
            model=model,
        )

    def build_prompt(self, data: dict):
        return (
            "You are the Operations Agent for a operations dashboard.\n"
            "Analyze the following operations summary data."
            "Focus only on insights that are genuinely meaningful. "
            "Base your observations on what the data clearly suggests, and avoid speculation. "
            "Prioritize clarity and usefulness over completeness.\n\n"
            f"DATA:\n{json.dumps(data, indent=2)}"
        )
