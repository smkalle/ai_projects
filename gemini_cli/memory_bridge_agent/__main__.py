"""Command-line entry point for Memory Bridge prototype runs."""

from __future__ import annotations

import argparse

from .console import run_console
from .tools import create_memory_bridge_kit


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a caregiver-reviewed Memory Bridge kit from a JSON profile."
    )
    parser.add_argument(
        "profile_path",
        nargs="?",
        help="Path to a Memory Bridge JSON profile. Omit to open the demo console.",
    )
    args = parser.parse_args()
    if args.profile_path:
        print(create_memory_bridge_kit(args.profile_path))
    else:
        run_console()


if __name__ == "__main__":
    main()
