"""
cli.py

Interactive CLI for chatting with the Enterprise Agent.

Supports:
- Streaming or non-streaming agent responses
- Graceful startup and shutdown
- Switchable chat modes via CLI flags

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import argparse

from app.db.postgres import init_db
from app.enums.prompts import JsonKey
from app.lib.agent.agent_runner import AgentRunner

agent = AgentRunner()


def main():
    parser = argparse.ArgumentParser(description="Enterprise Agent CLI")
    parser.add_argument(
        "--mode",
        choices=["run", "stream"],
        default="run",
        help="Chat mode: 'run' for full response, 'stream' for token streaming.",
    )
    args = parser.parse_args()

    print(f"Enterprise Agent CLI ({args.mode} mode). Type 'exit' to quit.")
    init_db()

    while True:
        query = input("You: ").strip()
        if query.lower() == "exit":
            print("Goodbye.")
            break

        if args.mode == "stream":
            stream = agent.stream(query)
            print("Agent (streaming): ", end="", flush=True)
            for chunk in stream:
                print(chunk, end="", flush=True)
            print()  # Newline after stream ends
        else:
            result = agent.run(query)
            if "error" in result:
                print("Error:", result["error"])
            else:
                print("Agent:", result.get(JsonKey.RESPONSE, "[No response]"))


if __name__ == "__main__":
    main()
