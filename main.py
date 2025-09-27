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
    try:
        client = OpenRouterClient()
    except Exception as exc:  # pragma: no cover
        print("Error initializing OpenRouterClient:", exc)
        return 1

    # Load system prompt from prompt.txt if present
    prompt_path = Path(__file__).resolve().parent / "prompt.txt"
    try:
        system_prompt = prompt_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        system_prompt = "You are a helpful assistant."

    print("Type your prompt and press Enter. Empty line to quit.\n")
    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()  # newline after Ctrl+D/Ctrl+C
            break

        if not user_text:
            break

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ]

        try:
            reply = client.chat(messages=messages)
        except Exception as exc:  # pragma: no cover
            print("Error from OpenRouter:", exc)
            continue

        print(f"Assistant: {reply}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


