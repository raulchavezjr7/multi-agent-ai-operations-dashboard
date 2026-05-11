import json
import os
from pathlib import Path

import requests

from backend.log_helper import log_agent_event
from backend.overview_nosql_helper import update_overview

from ..rag_helper import rag_agent_resources
from .accounting_agent import AccountingAgent
from .inventory_agent import InventoryAgent
from .operations_agent import OperationsAgent
from .sales_agent import SalesAgent
from .support_agent import SupportAgent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_FILE = Path(f"{BASE_DIR}/../../database/schema.json")


#  This is the Supervisors Agents class
class SupervisorAgent:
    def __init__(self):
        self.model = "meta-llama-3.1-8b-instruct"
        self.conversation = []
        self.sales_agent = SalesAgent(model="phi-3.1-mini-4k-instruct")
        self.inventory_agent = InventoryAgent(model="phi-3.1-mini-4k-instruct")
        self.support_agent = SupportAgent(model="phi-3.1-mini-4k-instruct")
        self.accounting_agent = AccountingAgent(model="phi-3.1-mini-4k-instruct")
        self.operations_agent = OperationsAgent(model="phi-3.1-mini-4k-instruct")

    # This load the model on LM Studios
    def load_model(self, model_name: str):
        return requests.post(
            "http://127.0.0.1:1234/api/v1/models/load",
            json={"model": model_name},
        ).json()

    # This unloads the model from LM Studios
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

    # This is a helper function to unload model
    def end_task_mode(self):
        self.unload_model(self.model)
        self.conversation = []

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
            agent_name="Supervisor Agent",
            agent_role=agent_role,
            label=label,
            request_type=request_type,
            message_overview=message_overview,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            details={prompt_desc: prompt[:200]},
        )

    #  This functions triggers all agents to run for overview process.
    #  It also uses the responses to create a prompt to run supervisors overview query.
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

    # This functions call the model and awaits response for overview process.
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

    # This function calls model and awaits response for chat process
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

    # This function calls model and awaits response for chat process using semi-rag
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
            f"Please provide the final polished response based on the rules above. "
            f"Remember always present a short 'Sources Used' section using the SOURCES PROVIDED. "
            f"Use a new line for the source used."
        )

        self.conversation.append({"role": "user", "content": combined_input})

        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Supervisor Agent for an operations dashboard that sometimes gets context from a RAG agent. "
                    "You receive two inputs: (1) the user's question and (2) an answer produced by a RAG worker. "
                    "Your job is to produce a final response for the user. "
                    "You might not get context from the RAG agent, if so response as you are a regular chat bot"
                    "Rules:\n"
                    "- Format text if properly"
                    "- Integrate or infer based on the RAG information if applicable.\n"
                    "- Always present a short 'Sources Used' section using the SOURCES PROVIDED.\n"
                    "- If no RAG agent context is present, then respond without it, but tell the user you did not get RAG context.\n\n"
                    "- Present a short 'Sources Used' section at the end.\n"
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

    # This function calls model and awaits response for chat process using full rag
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
            f"You must provide the final polished response based on the rules above."
            f"Remember always present a short 'Sources Used' section using the SOURCES PROVIDED section."
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
                    "- Always present a short 'Sources Used' section using the SOURCES PROVIDED section.\n"
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

    # This function calls model and awaits response for creating new charts in visualization tab
    def call_chart_llm(self, prompt: str):

        self.conversation.append({"role": "user", "content": prompt})
        schema = json.loads(SCHEMA_FILE.read_text())

        chartDefObject = (
            "{"
            '"id": string, '
            '"name": string, '
            '"sql": string, '
            '"type": string, '
            '"xField": string, '
            '"yField": string, '
            '"color"?: string, '
            '"colors"?: string[] '
            "}"
        )

        chartDefObjectExplanation = (
            "id is a unique identifier, snake_case, add random number to id for uniqueness \n"
            "name is a human-readable chart name \n"
            "sql is a valid SQLite SELECT query \n"
            "type is either a bar, line, area, region, heatmap, or pie \n"
            "xField is a column name used for x-axis or category \n"
            "yField is a column name used for y-axis or value \n"
            "color is a single color (hex) that is only used in bar, line, area, and region \n"
            "colors is a multiple colors only for pie \n"
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "Your ONLY job is to output a valid ChartDef object to help the user with creating new visualization charts. "
                    f"Database Schema: {schema}"
                    f"ChartDef Object Format: {chartDefObject}"
                    f"ChartDef Object Rules: {chartDefObjectExplanation}"
                    "Rules: "
                    "You MUST return a ChartDef Object in the exact format shown in the brackets of ChartDef Object Format. "
                    "You MUST NOT return explanations, reasoning, markdown, or commentary. "
                    "You MUST reference only tables and columns that exist in the schema. "
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
