"""
run_all.py — MiniMax M2.7 Tutorial Suite Master Runner
═══════════════════════════════════════════════════════
Usage:
    python run_all.py              # interactive module picker
    python run_all.py --all        # run every module in sequence
    python run_all.py --module 04  # run a specific module by ID
    python run_all.py --list       # print module list and exit

Modules:
    01  Hello World           Basic text generation + metadata inspection
    02  Streaming             Real-time streaming with TTFT measurement
    03  Multi-Turn Chat       Conversation history + context management
    04  Tool Use              Function calling + agentic tool loop
    05  Extended Thinking     Reasoning tokens + thinking budget
    06  System Prompting      Structured prompts, few-shot, dynamic construction
    07  Cost Tracking         CostLedger, budget guards, cache savings
    08  Agent ReAct Loop      Full ReAct agent with scratchpad and multi-tool
"""
import sys, argparse, importlib.util, os
from pathlib import Path

from config import MODULES
from utils import print_header, print_divider, log


def load_and_run(module_id: str) -> None:
    """Dynamically import and run a tutorial module by its 2-digit ID."""
    entry = next((m for m in MODULES if m["id"] == module_id), None)
    if not entry:
        log("ERROR", f"Module '{module_id}' not found. Run --list to see options.")
        sys.exit(1)

    file_path = Path(__file__).parent / entry["file"]
    if not file_path.exists():
        log("ERROR", f"Module file not found: {file_path}")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location(f"module_{module_id}", file_path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.run()


def print_module_list() -> None:
    print_divider("Available Modules")
    tag_colours = {
        "basic":        "\033[36m",
        "streaming":    "\033[33m",
        "conversation": "\033[34m",
        "agentic":      "\033[35m",
        "reasoning":    "\033[90m",
        "prompting":    "\033[32m",
        "production":   "\033[31m",
    }
    RESET = "\033[0m"
    for m in MODULES:
        colour = tag_colours.get(m["tag"], "")
        print(f"  {m['id']}  {m['name']:<24}  {colour}[{m['tag']}]{RESET}")
    print()


def interactive_picker() -> str:
    """Show the module list and prompt for a choice."""
    print_module_list()
    while True:
        choice = input("  Enter module ID (01–08) or 'all' to run everything: ").strip()
        if choice.lower() == "all":
            return "all"
        if any(m["id"] == choice for m in MODULES):
            return choice
        print(f"  Invalid choice '{choice}'. Try again.")


def main() -> None:
    print_header(
        "MiniMax M2.7 Tutorial Suite",
        "8 modules covering text, streaming, tools, thinking, agents, and cost"
    )

    parser = argparse.ArgumentParser(description="MiniMax M2.7 Tutorial Runner")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all",    action="store_true", help="Run all modules")
    group.add_argument("--module", metavar="ID",        help="Run a single module by ID")
    group.add_argument("--list",   action="store_true", help="List modules and exit")
    args = parser.parse_args()

    if args.list:
        print_module_list()
        return

    if args.module:
        target = args.module.zfill(2)
        log("INIT", f"Running module {target}")
        load_and_run(target)
        return

    if args.all:
        log("INIT", f"Running all {len(MODULES)} modules")
        for m in MODULES:
            load_and_run(m["id"])
            print_divider()
        log("DONE", "All modules complete")
        return

    # Interactive mode
    choice = interactive_picker()
    if choice == "all":
        for m in MODULES:
            load_and_run(m["id"])
            print_divider()
        log("DONE", "All modules complete")
    else:
        load_and_run(choice)


if __name__ == "__main__":
    main()
