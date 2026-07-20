from __future__ import annotations

import argparse
import json
import secrets
import subprocess
from pathlib import Path

from self_healing.policy import TriageResult, validate_changed_files


def capture(*command: str) -> str:
    return subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout


def write_output(path: Path, name: str, value: str) -> None:
    delimiter = f"SELF_HEALING_{secrets.token_hex(12)}"
    with path.open("a", encoding="utf-8") as output:
        output.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")


def bundle(
    result_path: Path,
    patch_path: Path,
    repository: str,
) -> bool:
    result = TriageResult.from_dict(json.loads(result_path.read_text(encoding="utf-8")))
    if not result.satisfies_repair_gate(repository):
        print("Claude result did not satisfy the repair gate; no patch was bundled.")
        return False

    subprocess.run(("git", "diff", "--check"), check=True)
    status = capture("git", "status", "--porcelain", "--untracked-files=all")
    unexpected = [
        line for line in status.splitlines() if line.startswith("?? ") and line != "?? triage-result.json"
    ]
    if unexpected:
        raise ValueError(f"Claude created untracked files: {unexpected!r}")
    actual = tuple(capture("git", "diff", "--name-only", "--diff-filter=ACMRTUXB").splitlines())
    validate_changed_files(result.changed_files, actual)

    patch = subprocess.run(
        ("git", "diff", "--binary", "--full-index"),
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    if not patch:
        raise ValueError("Claude reported a repair but produced an empty patch")
    patch_path.write_bytes(patch)
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--patch", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--github-output", type=Path, required=True)
    args = parser.parse_args()

    ready = bundle(args.result, args.patch, args.repository)
    write_output(args.github_output, "repair_ready", str(ready).lower())


if __name__ == "__main__":
    main()
