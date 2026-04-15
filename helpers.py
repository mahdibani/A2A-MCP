import os
import warnings
from typing import Any

import nest_asyncio
from IPython.display import Markdown, display
from dotenv import load_dotenv

try:
    from a2a.types import AgentCard
except ImportError:
    AgentCard = Any


def setup_env() -> None:
    """Initializes the environment by loading .env and applying nest_asyncio."""
    load_dotenv(override=True)
    gemini_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise RuntimeError(
            "Set GEMINI_API_KEY or GOOGLE_API_KEY in .env before running the notebooks."
        )

    os.environ["GOOGLE_API_KEY"] = gemini_api_key
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "FALSE")
    nest_asyncio.apply()

    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)


def get_gemini_api_key() -> str:
    """Returns the Gemini API key from the environment."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Set GEMINI_API_KEY or GOOGLE_API_KEY in .env before running the notebooks."
        )
    return api_key


def get_gemini_model(default: str = "gemini-2.5-flash-lite") -> str:
    """Returns the configured Gemini model for workshop examples."""
    return os.getenv("GEMINI_MODEL", default)


def get_gemini_openai_base_url() -> str:
    """Returns the OpenAI-compatible Gemini endpoint used by LangChain."""
    return os.getenv(
        "GEMINI_OPENAI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta/openai/",
    )


def display_agent_card(agent_card: AgentCard) -> None:
    """Nicely formats and displays an AgentCard."""

    def esc(text: str) -> str:
        """Escapes pipe characters for Markdown table compatibility."""
        return str(text).replace("|", r"\|")

    # --- Part 1: Main Metadata Table ---
    md_parts = [
        "### Agent Card Details",
        "| Property | Value |",
        "| :--- | :--- |",
        f"| **Name** | {esc(agent_card.name)} |",
        f"| **Description** | {esc(agent_card.description)} |",
        f"| **Version** | `{esc(agent_card.version)}` |",
        f"| **URL** | [{esc(agent_card.url)}]({agent_card.url}) |",
        f"| **Protocol Version** | `{esc(agent_card.protocol_version)}` |",
    ]

    # --- Part 2: Skills Table ---
    if agent_card.skills:
        md_parts.extend(
            [
                "\n#### Skills",
                "| Name | Description | Examples |",
                "| :--- | :--- | :--- |",
            ]
        )
        for skill in agent_card.skills:
            examples_str = (
                "<br>".join(f"- {esc(ex)}" for ex in skill.examples)
                if skill.examples
                else "N/A"
            )
            md_parts.append(
                f"| **{esc(skill.name)}** | {esc(skill.description)} | {examples_str} |"
            )

    # Join all parts and display
    display(Markdown("\n".join(md_parts)))
