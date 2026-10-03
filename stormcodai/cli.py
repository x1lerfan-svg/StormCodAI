from .agent import CodingAgent
from .config import Config
from .model_client import ModelClient
from .workspace import Workspace

def main():
    agent = CodingAgent(ModelClient(Config.from_env()), Workspace())
    print("StormCodAI 0.1.0 — AI coding agent")
    print("Type 'exit' to quit.\n")
    while True:
        try:
            request = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if request.lower() in {"exit", "quit"}:
            break
        if not request:
            continue
        try:
            print("\nStormCodAI > " + agent.ask(request) + "\n")
        except Exception as exc:
            print(f"\nError: {exc}\n")
