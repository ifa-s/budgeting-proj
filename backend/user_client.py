from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.AIM import OpenRouterClient
from backend.command_translator import CommandTranslator


class UserClient:
    """High-level session manager for the budgeting app.

    Encapsulates frontend/backend LLM clients, conversation state, and a BucketManager
    accessed via CommandTranslator.
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
        self.command_translator: CommandTranslator = CommandTranslator()
        # Resolve system prompts (fallback to files if not provided)
        project_dir = Path(__file__).resolve().parents[1]
        frontend_path = project_dir / "promptfrontend.txt"
        backend_path = project_dir / "promptbackend.txt"

        if frontend_system_prompt is None:
            if frontend_path.exists():
                frontend_system_prompt = frontend_path.read_text(encoding="utf-8").strip()
            else:
                frontend_system_prompt = (
                    "You are an expert financial advisor for a generation Z adult."
                )

        if backend_system_prompt is None:
            if backend_path.exists():
                backend_system_prompt = backend_path.read_text(encoding="utf-8").strip()
            else:
                backend_system_prompt = (
                    "You are the backend command planner for a budgeting app."
                )

        self.frontend_system_prompt: str = frontend_system_prompt
        self.backend_system_prompt: str = backend_system_prompt + "\n\n" + self.get_status()

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

    def start_conversation(self) -> str:
        reply = self.frontend.chat(
            messages=self.frontend_messages,
            model=self.frontend_model,
        )
        self.frontend_messages.append({"role": "assistant", "content": reply})
        return reply

    def process_user_input(self, user_text: str) -> Dict[str, str]:
        self.frontend_messages.append({"role": "user", "content": user_text})
        frontend_reply = self.frontend.chat(
            messages=self.frontend_messages,
            model=self.frontend_model,
        )
        self.frontend_messages.append({"role": "assistant", "content": frontend_reply})

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

        command_results = self.command_translator(backend_reply) if backend_reply else ""

        return {
            "frontend": frontend_reply,
            "backend": backend_reply,
            "commands": command_results,
        }

    def get_status(self) -> str:
        return self.command_translator.get_status()

    def get_bucket_manager_summary(self) -> str:
        total_pct = self.bucket_manager.get_total_percentage()
        total_budget = self.bucket_manager.get_total_budget()
        bucket_names = ", ".join(sorted(self.bucket_manager.get_bucket_names()))
        return (
            f"Budget=${total_budget:.2f} | Total%={total_pct:.2f} | Buckets=[{bucket_names}]"
        )


