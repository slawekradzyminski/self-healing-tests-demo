from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from self_healing.policy import TriageResult, validate_changed_files


def run(*command: str, capture: bool = False) -> str:
    result = subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
    )
    return result.stdout if capture else ""


def tracked_changes() -> tuple[str, ...]:
    output = run("git", "diff", "--name-only", "--diff-filter=ACMRTUXB", capture=True)
    return tuple(line for line in output.splitlines() if line)


def reject_untracked_files() -> None:
    output = run("git", "status", "--porcelain", "--untracked-files=all", capture=True)
    unexpected = [
        line for line in output.splitlines() if line.startswith("?? ") and line != "?? triage-result.json"
    ]
    if unexpected:
        raise ValueError(f"Repair created untracked files: {unexpected!r}")


def publish(result_path: Path, patch_path: Path, repository: str, repo_dir: Path) -> bool:
    os.chdir(repo_dir)
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    result = TriageResult.from_dict(payload)

    if not result.satisfies_repair_gate(repository):
        print("Claude result did not satisfy the repair gate.")
        return False

    run("git", "apply", "--check", str(patch_path))
    run("git", "apply", str(patch_path))
    run("git", "diff", "--check")
    reject_untracked_files()
    changed_files = validate_changed_files(result.changed_files, tracked_changes())

    run("npm", "run", "typecheck")
    run("npm", "run", "test:e2e")

    run("git", "config", "user.name", "claude[bot]")
    run(
        "git",
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
    )
    run("git", "add", "--", *changed_files)
    run("git", "commit", "-m", "Fix E2E test defect diagnosed by Claude")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--patch", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--repo-dir", type=Path, required=True)
    args = parser.parse_args()
    publish(
        args.result.resolve(),
        args.patch.resolve(),
        args.repository,
        args.repo_dir.resolve(),
    )


if __name__ == "__main__":
    main()
