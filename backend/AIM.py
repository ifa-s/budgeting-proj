from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI


class OpenRouterClient:
    """Thin wrapper around OpenRouter's OpenAI-compatible API.

    Reads `OPENROUTER_API_KEY` from a `.env` file (kept out of Git) or the environment.

    Example:

        client = OpenRouterClient()
        reply = client.chat(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ]
        )
        print(reply)
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
    ) -> None:
        # Load `.env` from project root if present
        project_root = Path(__file__).resolve().parents[1]
        dotenv_path = project_root / ".env"
        if dotenv_path.exists():
            load_dotenv(dotenv_path)
        else:
            # Fall back to default search (current working directory)
            load_dotenv()

        self.api_key: str = api_key or os.getenv("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise RuntimeError(
                "Missing OPENROUTER_API_KEY. Set it in .env or the environment."
            )

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

    def chat(
        self,
        *,
        messages: List[Dict[str, Any]],
        model: str = "google/gemini-2.5-flash-lite",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> str:
        """Send a chat completion request and return the assistant's text content.

        - `messages`: List of {role, content} per OpenAI spec
        - `model`: Any model available on OpenRouter (default: openrouter/auto)
        - `json_mode`: If True, requests a JSON object response format
        """
        response_format = {"type": "json_object"} if json_mode else None

        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,  # type: ignore[arg-type]
        )

        choice = completion.choices[0]
        # Prefer `message.content` when present; fall back to tool outputs
        content = getattr(choice.message, "content", None)
        if content:
            return content
        # Graceful fallback for unexpected shapes
        return ""

    def list_models(self) -> List[str]:
        """Return available model IDs from OpenRouter."""
        models = self.client.models.list()
        return [m.id for m in models.data]

