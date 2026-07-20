from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path


SAFE_BRANCH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")


def repair_branch(run_id: str) -> str:
    if not run_id.isdigit():
        raise ValueError("run_id must be numeric")
    return f"claude/e2e-repair-{run_id}"


def validate_branch(branch: str) -> str:
    if not SAFE_BRANCH.fullmatch(branch) or branch.endswith("/") or ".." in branch:
        raise ValueError(f"Unsafe branch name: {branch!r}")
    if branch == "main":
        raise ValueError("The repair publisher never pushes directly to main")
    return branch


def run(*command: str, cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def deliver(
    event_name: str,
    repository: str,
    repo_dir: Path,
    head_branch: str | None,
    run_id: str,
) -> None:
    if "GH_TOKEN" not in os.environ:
        raise ValueError("GH_TOKEN is required only for the delivery step")

    run("gh", "auth", "setup-git", cwd=repo_dir)

    if event_name == "pull_request":
        branch = validate_branch(head_branch or "")
        run("git", "push", "origin", f"HEAD:{branch}", cwd=repo_dir)
        return

    branch = validate_branch(repair_branch(run_id))
    run("git", "push", "origin", f"HEAD:refs/heads/{branch}", cwd=repo_dir)
    run(
        "gh",
        "pr",
        "create",
        "--repo",
        repository,
        "--draft",
        "--base",
        "main",
        "--head",
        branch,
        "--title",
        "Fix E2E test defect diagnosed by Claude",
        "--body",
        "Automated draft repair. Review the linked failing run, triage artifact, and verification before merging.",
        cwd=repo_dir,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--repo-dir", type=Path, required=True)
    parser.add_argument("--head-branch")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    deliver(
        args.event,
        args.repository,
        args.repo_dir.resolve(),
        args.head_branch,
        args.run_id,
    )


if __name__ == "__main__":
    main()
