from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from self_healing.config import claude_arguments, load_prompt


METADATA_FIELDS = (
    "type",
    "subtype",
    "is_error",
    "duration_ms",
    "duration_api_ms",
    "num_turns",
    "total_cost_usd",
    "usage",
    "modelUsage",
    "permission_denials",
    "errors",
)


def extract_structured_output(payload: dict[str, Any]) -> dict[str, Any]:
    structured = payload.get("structured_output")
    if isinstance(structured, dict):
        return structured

    result = payload.get("result")
    if isinstance(result, str):
        try:
            decoded = json.loads(result)
        except json.JSONDecodeError as error:
            raise ValueError("Claude did not return structured JSON") from error
        if isinstance(decoded, dict):
            return decoded

    raise ValueError("Claude output is missing structured_output")


def select_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    return {name: payload[name] for name in METADATA_FIELDS if name in payload}


def describe_run(returncode: int, metadata: dict[str, Any]) -> str:
    return (
        "Claude Code process: "
        f"exit={returncode} "
        f"subtype={metadata.get('subtype', 'unknown')} "
        f"is_error={metadata.get('is_error', 'unknown')} "
        f"turns={metadata.get('num_turns', 'unknown')} "
        f"cost_usd={metadata.get('total_cost_usd', 'unknown')}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--executable", default="claude")
    args = parser.parse_args()

    completed = subprocess.run(
        [args.executable, *claude_arguments(), load_prompt()],
        check=False,
        stdout=subprocess.PIPE,
        text=True,
    )
    if not completed.stdout.strip():
        raise RuntimeError(f"Claude Code exited with status {completed.returncode} and no JSON output")

    payload = json.loads(completed.stdout)
    metadata = select_metadata(payload)
    args.metadata.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(describe_run(completed.returncode, metadata), flush=True)

    if completed.returncode != 0:
        raise RuntimeError(f"Claude Code exited with status {completed.returncode}")

    structured = extract_structured_output(payload)
    args.result.write_text(json.dumps(structured, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
