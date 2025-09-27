from __future__ import annotations

from typing import Dict

from user_client import UserClient


def main() -> int:
    # Initialize high-level user client
    try:
        client = UserClient()
    except Exception as exc:  # pragma: no cover
        print("Error initializing UserClient:", exc)
        return 1

    print("Type your prompt and press Enter. Empty line to quit.\n")

    # Prime the frontend and show initial assistant message
    try:
        reply = client.start_conversation()
    except Exception as exc:  # pragma: no cover
        print("Error from frontend model:", exc)
        return 1
    print(f"Assistant: {reply}\n")

    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()  # newline after Ctrl+D/Ctrl+C
            break

        if not user_text:
            break

        # Process via frontend + backend + execute planned commands
        try:
            result: Dict[str, str] = client.process_user_input(user_text)
        except Exception as exc:  # pragma: no cover
            print("Error processing input:", exc)
            continue

        print(f"🎯 FRONTEND: {result.get('frontend', '')}\n")
        print(f"⚙️ BACKEND: {result.get('backend', '')}\n")

        commands_output = result.get("commands", "")
        if commands_output:
            print(f"🧰 COMMANDS:\n{commands_output}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())