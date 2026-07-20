from __future__ import annotations

import json
import shlex
from pathlib import Path


AUTOMATION_ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = AUTOMATION_ROOT / "prompts" / "e2e-failure.md"
SCHEMA_PATH = AUTOMATION_ROOT / "schemas" / "triage-result.schema.json"

MAX_TURNS = 35


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8").strip()


def load_schema() -> dict[str, object]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def render_claude_args() -> str:
    schema = json.dumps(load_schema(), separators=(",", ":"))
    return " ".join(
        (
            f"--max-turns {MAX_TURNS}",
            "--permission-mode bypassPermissions",
            "--dangerously-skip-permissions",
            f"--json-schema {shlex.quote(schema)}",
        )
    )
