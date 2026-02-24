import requests
import json
from .accounting_agent import AccountingAgent
from .inventory_agent import InventoryAgent
from .operations_agent import OperationsAgent
from .sales_agent import SalesAgent
from .support_agent import SupportAgent


class SupervisorAgent:
    def __init__(self):
        self.model = "meta-llama-3.1-8b-instruct"

        self.sales_agent = SalesAgent(model="phi-3.1-mini-4k-instruct")
        self.inventory_agent = InventoryAgent(model="phi-3.1-mini-4k-instruct")
        self.support_agent = SupportAgent(model="phi-3.1-mini-4k-instruct")
        self.accounting_agent = AccountingAgent(model="phi-3.1-mini-4k-instruct")
        self.operations_agent = OperationsAgent(model="phi-3.1-mini-4k-instruct")

    def run_all(self):
        results = {
            "sales": self.sales_agent.run(),
            "inventory": self.inventory_agent.run(),
            "support": self.support_agent.run(),
            "accounting": self.accounting_agent.run(),
            "operations": self.operations_agent.run(),
        }

        prompt = (
            "You are the Supervisor Agent for a operation dashboard. Combine the insights from all domain agents. "
            "Provide a clear, meaningful, concise summary of the overall business situation. "
            "Highlight important patterns, risks, and opportunities.\n\n"
            f"Sales Insight:\n{results['sales']}\n\n"
            f"Inventory Insight:\n{results['inventory']}\n\n"
            f"Support Insight:\n{results['support']}\n\n"
            f"Accounting Insight:\n{results['accounting']}\n\n"
            f"Operations Insight:\n{results['operations']}\n\n"
        )
        return self.call_llm(prompt)

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
                                "You are the Supervisor Agent for a operation dashboard."
                                "Keep responses concise, structured, and under 500 tokens."
                                "Avoid filler, avoid repeating the prompt, and keep responses concise."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500,
                },
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"LLM error {e}"
