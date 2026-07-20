from __future__ import annotations

import argparse
import secrets
from pathlib import Path

from self_healing.config import load_prompt, render_claude_args


def write_output(path: Path, name: str, value: str) -> None:
    delimiter = f"SELF_HEALING_{secrets.token_hex(12)}"
    with path.open("a", encoding="utf-8") as output:
        output.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--github-output", type=Path, required=True)
    args = parser.parse_args()

    write_output(args.github_output, "prompt", load_prompt())
    write_output(args.github_output, "claude_args", render_claude_args())


if __name__ == "__main__":
    main()
