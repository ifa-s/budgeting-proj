from __future__ import annotations

import sys
from typing import List, Dict, Any
from pathlib import Path

try:
    from backend.AIM import OpenRouterClient
except Exception as exc:  # pragma: no cover
    print("Failed to import OpenRouterClient from backend.AIM:", exc)
    sys.exit(1)


def main() -> int:
    # Initialize frontend client
    try:
        frontend = OpenRouterClient()
    except Exception as exc:  # pragma: no cover
        print("Error initializing Frontend OpenRouterClient:", exc)
        return 1

    # Initialize backend client
    try:
        backend = OpenRouterClient()
    except Exception as exc:  # pragma: no cover
        print("Error initializing Backend OpenRouterClient:", exc)
        return 1

    # Load frontend system prompt
    frontend_prompt_path = Path(__file__).resolve().parent / "promptfrontend.txt"
    try:
        frontend_system_prompt = frontend_prompt_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        frontend_system_prompt = "You are an expert financial advisor for a generation Z adult."
    
    # Load backend system prompt
    backend_prompt_path = Path(__file__).resolve().parent / "promptbackend.txt"
    try:
        backend_system_prompt = backend_prompt_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        backend_system_prompt = "You are the backend command planner for a budgeting app."
    
    print("Type your prompt and press Enter. Empty line to quit.\n")
    
    # Initialize frontend conversation context
    frontend_messages: List[Dict[str, Any]] = [
        {"role": "system", "content": frontend_system_prompt},
    ]
    try:
        reply = frontend.chat(messages=frontend_messages)
    except Exception as exc:  # pragma: no cover
        print("Error from OpenRouter:", exc)
        return 1
    print(f"Assistant: {reply}\n")
    # Add assistant's first reply to context
    frontend_messages.append({"role": "assistant", "content": reply})

    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()  # newline after Ctrl+D/Ctrl+C
            break

        if not user_text:
            break

        # Add user message to frontend context
        frontend_messages.append({"role": "user", "content": user_text})

        # Call frontend (financial advisor)
        try:
            frontend_reply = frontend.chat(messages=frontend_messages)
            print(f"🎯 FRONTEND: {frontend_reply}\n")
        except Exception as exc:  # pragma: no cover
            print("Error from Frontend OpenRouter:", exc)
            frontend_reply = ""
            # Remove the last user message if the request failed
            frontend_messages.pop()
            continue
        
        # Add frontend reply to context
        frontend_messages.append({"role": "assistant", "content": frontend_reply})
        
        # Call backend (command planner) with frontend response
        backend_messages: List[Dict[str, Any]] = [
            {"role": "system", "content": backend_system_prompt},
            {"role": "user", "content": f"USER_REQUEST: {user_text}\nLLM_RESPONSE: {frontend_reply}"},
        ]
        try:
            backend_reply = backend.chat(messages=backend_messages)
            print(f"⚙️ BACKEND: {backend_reply}\n")
        except Exception as exc:  # pragma: no cover
            print("Error from Backend OpenRouter:", exc)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())