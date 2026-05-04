import json
import os
from pathlib import Path

import requests

from backend.log_helper import log_agent_event
from backend.overview_nosql_helper import update_overview

from .accounting_agent import AccountingAgent
from .inventory_agent import InventoryAgent
from .operations_agent import OperationsAgent
from .rag_agent import rag_agent_resources
from .sales_agent import SalesAgent
from .support_agent import SupportAgent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_FILE = Path(f"{BASE_DIR}/../../database/schema.json")


class SupervisorAgent:
    def __init__(self):
        self.model = "meta-llama-3.1-8b-instruct"
        self.conversation = []
        self.sales_agent = SalesAgent(model="phi-3.1-mini-4k-instruct")
        self.inventory_agent = InventoryAgent(model="phi-3.1-mini-4k-instruct")
        self.support_agent = SupportAgent(model="phi-3.1-mini-4k-instruct")
        self.accounting_agent = AccountingAgent(model="phi-3.1-mini-4k-instruct")
        self.operations_agent = OperationsAgent(model="phi-3.1-mini-4k-instruct")

    def load_model(self, model_name: str):
        return requests.post(
            "http://127.0.0.1:1234/api/v1/models/load",
            json={"model": model_name},
        ).json()

    def unload_model(self, model_name: str):
        try:
            response = requests.get("http://127.0.0.1:1234/api/v1/models")
            models = response.json().get("models", [])
            instance_id = ""

            for model in models:
                if (
                    model.get("display_name") == model_name
                    or model.get("key") == model_name
                ):
                    instance_id = model["loaded_instances"][0]["id"]

            print(instance_id)
            unload_response = requests.post(
                "http://127.0.0.1:1234/api/v1/models/unload",
                json={"instance_id": instance_id},
            )
            unload_response.raise_for_status()

        except Exception as e:
            return f"Unload error {e}"

    def end_task_mode(self):
        self.unload_model(self.model)
        self.conversation = []

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
            agent_name="Supervisor Agent",
            agent_role=agent_role,
            label=label,
            request_type=request_type,
            message_overview=message_overview,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            details={prompt_desc: prompt[:200]},
        )

    def run_all(self):

        results = {
            "sales": self.sales_agent.run(),
            "inventory": self.inventory_agent.run(),
            "support": self.support_agent.run(),
            "accounting": self.accounting_agent.run(),
            "operations": self.operations_agent.run(),
        }

        update_overview(1, {"sales": results["sales"]})
        update_overview(2, {"inventory": results["inventory"]})
        update_overview(3, {"support": results["support"]})
        update_overview(4, {"accounting": results["accounting"]})
        update_overview(5, {"operations": results["operations"]})

        prompt = (
            "You are the Supervisor Agent for a operation dashboard. Combine the insights from all domain agents."
            "Provide a clear, meaningful, concise summary of the overall business situation. "
            "Highlight important patterns, risks, and opportunities.\n\n"
            f"Sales Insight:\n{results['sales']}\n\n"
            f"Inventory Insight:\n{results['inventory']}\n\n"
            f"Support Insight:\n{results['support']}\n\n"
            f"Accounting Insight:\n{results['accounting']}\n\n"
            f"Operations Insight:\n{results['operations']}\n\n"
        )
        return self.call_llm_overview(prompt)

    def call_llm_overview(self, prompt: str):

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
                                "Keep responses concise, structured, and under 600 tokens."
                                "Avoid filler, avoid repeating the prompt, and keep responses concise."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 800,
                },
                timeout=480,
            )
            response.raise_for_status()
            result = response.json()
            update_overview(
                6, {"supervisor": result["choices"][0]["message"]["content"]}
            )

            self.log_agent(
                "supervisor",
                "Processed",
                "prompt",
                "Daily overview request",
                int(result["usage"]["prompt_tokens"]),
                0,
                "prompt_preview",
                prompt,
            )
            self.log_agent(
                "supervisor",
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
                "supervisor",
                "ERROR",
                "error",
                "Failed daily response",
                0,
                0,
                "error details",
                error_msg,
            )
            return f"LLM error {error_msg}"

    def call_llm(self, prompt: str):

        self.conversation.append({"role": "user", "content": prompt})
        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Supervisor Agent for a operation dashboard."
                    "You are not using a rag pipeline."
                    "Keep responses concise, structured, and under 800 tokens."
                    "Avoid filler, avoid repeating the prompt, and keep responses concise."
                    "Format text if properly"
                ),
            },
            *self.conversation,
        ]

        try:
            response = requests.post(
                "http://127.0.0.1:1234/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 800,
                },
                timeout=240,
            )
            response.raise_for_status()
            result = response.json()

            self.conversation.append(
                {
                    "role": "assistant",
                    "content": result["choices"][0]["message"]["content"],
                }
            )
            self.log_agent(
                "supervisor",
                "Processed",
                "prompt",
                "Supervisor request",
                int(result["usage"]["prompt_tokens"]),
                0,
                "prompt_preview",
                prompt,
            )
            self.log_agent(
                "supervisor",
                "Processed",
                "response",
                "Supervisor response",
                0,
                int(result["usage"]["total_tokens"]),
                "response_preview",
                result["choices"][0]["message"]["content"],
            )
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            error_msg = f"Failed at LLM response: {str(e)}"
            self.log_agent(
                "supervisor",
                "ERROR",
                "error",
                "Failed supervisor response",
                0,
                0,
                "error details",
                error_msg,
            )
            return f"LLM error {error_msg}"

    def call_llm_semi_rag(self, prompt: str):

        rag_results = rag_agent_resources(prompt)
        answer = rag_results["answer"]
        sources = rag_results["sources"]

        if sources:
            source_list = "\n".join(
                f"- {src.get('file', 'unknown')}" for src in sources
            )
            rag_context = (
                f"RAG WORKER OUTPUT:\n{answer}\n\nSOURCES PROVIDED:\n{source_list}"
            )
        else:
            rag_context = (
                f"RAG WORKER OUTPUT:\n{answer}\n\nNo internal documents were relevant."
            )

        combined_input = (
            f"USER QUESTION: {prompt}\n\n"
            f"{rag_context}\n\n"
            f"Please provide the final polished response based on the rules above."
            f"Remember always present a short 'Sources Used' section at the end indicating what Rag worker output."
            f"Use a new line for the source used."
        )

        self.conversation.append({"role": "user", "content": combined_input})

        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Supervisor Agent for an operations dashboard. "
                    "You receive two inputs: (1) the user's question and (2) an answer produced by a RAG worker. "
                    "Your job is to produce a final response for the user."
                    "If no RAG input is present, then give a response without it, but tell the user you are not using RAG.\n\n"
                    "Rules:\n"
                    "- Format text if properly"
                    "- Integrate or infer based on the RAG information if applicable.\n"
                    "- Always present a short 'Sources Used' section at the end indicating what Rag worker output.\n"
                    "- Present a short 'Sources Used' section at the end.\n"
                    "- If no internal documents were used, state that clearly.\n"
                    "- Keep responses concise, professional, and under 800 tokens.\n"
                    "- Do not repeat the user prompt or use filler phrases."
                ),
            },
            *self.conversation,
        ]

        try:
            response = requests.post(
                "http://127.0.0.1:1234/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 800,
                },
                timeout=480,
            )
            response.raise_for_status()
            result = response.json()

            self.conversation.append(
                {
                    "role": "assistant",
                    "content": result["choices"][0]["message"]["content"],
                }
            )

            self.log_agent(
                "supervisor",
                "Processed",
                "prompt",
                "Semi-rag supervisors request",
                int(result["usage"]["prompt_tokens"]),
                0,
                "prompt_preview",
                prompt,
            )
            self.log_agent(
                "supervisor",
                "Processed",
                "response",
                "Semi-rag supervisors response",
                0,
                int(result["usage"]["total_tokens"]),
                "response_preview",
                result["choices"][0]["message"]["content"],
            )
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            error_msg = f"Failed at LLM response: {str(e)}"
            self.log_agent(
                "supervisor",
                "ERROR",
                "error",
                "Failed Semi-rag supervisors response",
                0,
                0,
                "error details",
                error_msg,
            )
            return f"LLM error {error_msg}"

    def call_llm_rag(self, prompt: str):
        rag_results = rag_agent_resources(prompt)
        answer = rag_results["answer"]
        sources = rag_results["sources"]

        if sources:
            source_list = "\n".join(
                f"- {src.get('file', 'unknown')}" for src in sources
            )
            rag_context = (
                f"RAG WORKER OUTPUT:\n{answer}\n\nSOURCES PROVIDED:\n{source_list}"
            )
        else:
            rag_context = (
                f"RAG WORKER OUTPUT:\n{answer}\n\nNo internal documents were relevant."
            )

        combined_input = (
            f"USER QUESTION: {prompt}\n\n"
            f"{rag_context}\n\n"
            f"Please provide the final polished response based on the rules above."
            f"Remember always present a short 'Sources Used' section at the end indicating what Rag worker output."
            f"Use a new line for the source used."
        )

        self.conversation.append({"role": "user", "content": combined_input})

        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Supervisor Agent for an operations dashboard. "
                    "You receive two inputs: (1) the user's question and (2) an answer produced by a RAG worker. "
                    "Your job is to produce a final, polished response for the user.\n\n"
                    "Rules:\n"
                    "- Format text if properly"
                    "- Integrate RAG information clearly and accurately.\n"
                    "- Always present a short 'Sources Used' section at the end indicating what Rag worker output.\n"
                    "- If no internal documents were used, state that clearly.\n"
                    "- Keep responses concise, professional, and under 800 tokens.\n"
                    "- Do not repeat the user prompt or use filler phrases."
                ),
            },
            *self.conversation,
        ]

        try:
            response = requests.post(
                "http://127.0.0.1:1234/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 800,
                },
                timeout=480,
            )
            response.raise_for_status()
            result = response.json()

            self.conversation.append(
                {
                    "role": "assistant",
                    "content": result["choices"][0]["message"]["content"],
                }
            )

            self.log_agent(
                "supervisor",
                "Processed",
                "prompt",
                "Full-rag supervisors request",
                int(result["usage"]["prompt_tokens"]),
                0,
                "prompt_preview",
                prompt,
            )
            self.log_agent(
                "supervisor",
                "Processed",
                "response",
                "Full-rag supervisors response",
                0,
                int(result["usage"]["total_tokens"]),
                "response_preview",
                result["choices"][0]["message"]["content"],
            )
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            error_msg = f"Failed at LLM response: {str(e)}"
            self.log_agent(
                "supervisor",
                "ERROR",
                "error",
                "Failed Full-rag supervisors response",
                0,
                0,
                "error details",
                error_msg,
            )
            return f"LLM error {error_msg}"

    def call_chart_llm(self, prompt: str):

        self.conversation.append({"role": "user", "content": prompt})
        schema = json.loads(SCHEMA_FILE.read_text())

        chartDefObject = (
            "{"
            '"id": string,'
            '"name": string,'
            '"sql": string,'
            '"type": string,'
            '"xField": string,'
            '"yField": string,'
            '"color"?: string,'
            '"colors"?: string[]'
            "}"
        )

        chartDefObjectExplanation = (
            "id is a unique identifier, snake_case, add random number to id for uniqueness"
            "name is a human-readable chart name"
            "sql is a valid SQLite SELECT query"
            "type is either a bar, line, area, region, heatmap, or pie"
            "xField is a column name used for x-axis or category"
            "yField is a column name used for y-axis or value"
            "color is a single color (hex) that is only used in bar, line, area, and region"
            "colors is a multiple colors only for pie"
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "Your ONLY job is to output a valid ChartDef object to help the user with creating new visualization charts."
                    f"Database Schema: {schema}"
                    f"ChartDef Object Format: {chartDefObject}"
                    f"ChartDef Object Rules: {chartDefObjectExplanation}"
                    "Rules:"
                    "You MUST return a ChartDef Object in the exact format shown in the brackets of ChartDef Object Format"
                    "You MUST NOT return explanations, reasoning, markdown, or commentary."
                    "You MUST reference only tables and columns that exist in the schema."
                ),
            },
            *self.conversation,
        ]
        try:
            response = requests.post(
                "http://127.0.0.1:1234/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.5,
                    "max_tokens": 500,
                },
                timeout=240,
            )
            response.raise_for_status()
            result = response.json()

            self.log_agent(
                "supervisor",
                "Processed",
                "prompt",
                "Chart creation request",
                int(result["usage"]["prompt_tokens"]),
                0,
                "prompt_preview",
                prompt,
            )
            self.log_agent(
                "supervisor",
                "Processed",
                "response",
                "Chart creation response",
                0,
                int(result["usage"]["total_tokens"]),
                "response_preview",
                result["choices"][0]["message"]["content"],
            )
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            error_msg = f"Failed at LLM response: {str(e)}"
            self.log_agent(
                "supervisor",
                "ERROR",
                "error",
                "Failed Chart creation response",
                0,
                0,
                "error details",
                error_msg,
            )
            return f"LLM error {error_msg}"
