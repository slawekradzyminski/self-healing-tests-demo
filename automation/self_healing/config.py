from __future__ import annotations

import json
from pathlib import Path


AUTOMATION_ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = AUTOMATION_ROOT / "prompts" / "e2e-failure.md"
SCHEMA_PATH = AUTOMATION_ROOT / "schemas" / "triage-result.schema.json"

MAX_TURNS = 35
MAX_BUDGET_USD = 2.0
CLAUDE_CODE_VERSION = "2.1.158"


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8").strip()


def load_schema() -> dict[str, object]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def claude_arguments() -> tuple[str, ...]:
    schema = json.dumps(load_schema(), separators=(",", ":"))
    return (
        "-p",
        "--output-format",
        "json",
        "--max-turns",
        str(MAX_TURNS),
        "--max-budget-usd",
        str(MAX_BUDGET_USD),
        "--permission-mode",
        "bypassPermissions",
        "--dangerously-skip-permissions",
        "--no-session-persistence",
        "--json-schema",
        schema,
    )
