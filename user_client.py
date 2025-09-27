from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.AIM import OpenRouterClient
from command_translator import CommandTranslator


class UserClient:
    """High-level session manager for the budgeting app.

    Encapsulates:
    - Frontend LLM client (financial advisor persona)
    - Backend LLM client (command planner persona)
    - Conversation state for the frontend
    - Command translation and a shared BucketManager

    Typical usage:

        client = UserClient()
        first_reply = client.start_conversation()
        out = client.process_user_input("I make $4,000/mo and want to save more")
        print(out["frontend"])     # Advisor response
        print(out["backend"])      # Planned commands
        print(out["commands"])     # Execution results against BucketManager
        print(client.get_status())  # Current bucket status
    """

    def __init__(
        self,
        *,
        frontend_system_prompt: Optional[str] = None,
        backend_system_prompt: Optional[str] = None,
        frontend_model: str = "google/gemini-2.5-flash-lite",
        backend_model: str = "google/gemini-2.5-flash-lite",
    ) -> None:
        # Initialize LLM clients
        self.frontend: OpenRouterClient = OpenRouterClient()
        self.backend: OpenRouterClient = OpenRouterClient()

        # Resolve system prompts (fallback to files if not provided)
        project_dir = Path(__file__).resolve().parent
        if frontend_system_prompt is None:
            frontend_prompt_path = project_dir / "promptfrontend.txt"
            if frontend_prompt_path.exists():
                frontend_system_prompt = frontend_prompt_path.read_text(encoding="utf-8").strip()
            else:
                frontend_system_prompt = (
                    "You are an expert financial advisor for a generation Z adult."
                )

        if backend_system_prompt is None:
            backend_prompt_path = project_dir / "promptbackend.txt"
            if backend_prompt_path.exists():
                backend_system_prompt = backend_prompt_path.read_text(encoding="utf-8").strip()
            else:
                backend_system_prompt = (
                    "You are the backend command planner for a budgeting app."
                )

        self.frontend_system_prompt: str = frontend_system_prompt
        self.backend_system_prompt: str = backend_system_prompt

        # Track models per side (allow overrides)
        self.frontend_model: str = frontend_model
        self.backend_model: str = backend_model

        # Frontend conversation context
        self.frontend_messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.frontend_system_prompt},
        ]

        # Command translation + shared BucketManager
        self.command_translator: CommandTranslator = CommandTranslator()
        self.bucket_manager = self.command_translator.bucket_manager

    # ---- Conversation control -------------------------------------------------
    def start_conversation(self) -> str:
        """Prime the frontend and return its initial message."""
        reply = self.frontend.chat(
            messages=self.frontend_messages,
            model=self.frontend_model,
        )
        self.frontend_messages.append({"role": "assistant", "content": reply})
        return reply

    def process_user_input(self, user_text: str) -> Dict[str, str]:
        """Send `user_text` to the frontend, then plan via backend and execute.

        Returns a dict containing:
        - "frontend": the advisor response
        - "backend": the planned command string(s)
        - "commands": execution results from the CommandTranslator
        """
        # Frontend turn
        self.frontend_messages.append({"role": "user", "content": user_text})
        frontend_reply = self.frontend.chat(
            messages=self.frontend_messages,
            model=self.frontend_model,
        )
        self.frontend_messages.append({"role": "assistant", "content": frontend_reply})

        # Backend plan (conditioned on both the user text and the advisor reply)
        backend_messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.backend_system_prompt},
            {
                "role": "user",
                "content": f"USER_REQUEST: {user_text}\nLLM_RESPONSE: {frontend_reply}",
            },
        ]
        backend_reply = self.backend.chat(
            messages=backend_messages,
            model=self.backend_model,
        )

        # Execute planned commands, if any
        command_results = self.command_translator(backend_reply) if backend_reply else ""

        return {
            "frontend": frontend_reply,
            "backend": backend_reply,
            "commands": command_results,
        }

    # ---- Status helpers -------------------------------------------------------
    def get_status(self) -> str:
        """Return a formatted status string for the current BucketManager."""
        return self.command_translator.get_status()

    def get_bucket_manager_summary(self) -> str:
        """Return a concise single-line summary of bucket state."""
        total_pct = self.bucket_manager.get_total_percentage()
        total_budget = self.bucket_manager.get_total_budget()
        bucket_names = ", ".join(sorted(self.bucket_manager.get_bucket_names()))
        return (
            f"Budget=${total_budget:.2f} | Total%={total_pct:.2f} | Buckets=[{bucket_names}]"
        )


