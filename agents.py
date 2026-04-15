import base64
from pathlib import Path
import requests
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StdioConnection
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from helpers import (
    get_gemini_api_key,
    get_gemini_model,
    get_gemini_openai_base_url,
    setup_env,
)

SYSTEM_INSTRUCTION = (
    "You are an expert insurance agent designed to assist with coverage "
    "queries. Use the provided documents to answer questions about insurance "
    "policies. If the information is not available in the documents, respond "
    "with 'I don't know'."
)

class PolicyAgent:
    def __init__(self) -> None:
        setup_env()
        self.api_key = get_gemini_api_key()
        self.model = get_gemini_model()
        self.api_url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )
        with Path("./data/2026AnthemgHIPSBC.pdf").open("rb") as file:
            self.pdf_data = base64.standard_b64encode(file.read()).decode("utf-8")

    def answer_query(self, prompt: str) -> str:
        response = requests.post(
            self.api_url,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            json={
                "system_instruction": {
                    "parts": [{"text": SYSTEM_INSTRUCTION}]
                },
                "generationConfig": {"temperature": 0.2},
                "contents": [
                    {
                        "parts": [
                            {
                                "inline_data": {
                                    "mime_type": "application/pdf",
                                    "data": self.pdf_data,
                                }
                            },
                            {"text": prompt},
                        ]
                    }
                ],
            },
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"].replace("$", r"\\$")


class ProviderAgent:
    def __init__(self) -> None:
        setup_env()
        self.gemini_api_key = get_gemini_api_key()
        self.model = get_gemini_model()
        self.base_url = get_gemini_openai_base_url()

        self.mcp_client = MultiServerMCPClient(
            {
                "find_healthcare_providers": StdioConnection(
                    transport="stdio",
                    command="uv",
                    args=["run", "mcpserver.py"],
                )
            }
        )
        self.agent = None

    async def initialize(self):
        """Initialize the agent asynchronously."""
        tools = await self.mcp_client.get_tools()
        self.agent = create_react_agent(
            ChatOpenAI(
                model=self.model,
                openai_api_key=self.gemini_api_key,
                openai_api_base=self.base_url,
            ),
            tools,
            state_modifier="""Your task is to find and list providers using 
            the find_healthcare_providers MCP Tool based on the users query. 
            Only use providers based on the response from the tool. Output 
            the information in a table.""",
        )
        return self

    async def answer_query(self, prompt: str) -> str:
        if self.agent is None:
            raise RuntimeError(
                "Agent not initialized. Call initialize() first."
            )

        response = await self.agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ]
            }
        )
        return response["messages"][-1].content