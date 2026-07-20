from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def safe_text(value: object) -> str:
    return (
        str(value)
        .replace("@", "@\u200b")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("|", "\\|")
        .strip()
    )


def run_url(server_url: str, repository: str, run_id: str) -> str:
    return f"{server_url.rstrip('/')}/{repository}/actions/runs/{run_id}"


def bullet_list(values: object) -> str:
    if not isinstance(values, list) or not values:
        return "- None reported"
    return "\n".join(f"- {safe_text(value).replace(chr(10), ' ')}" for value in values)


def quote(value: object) -> str:
    lines = safe_text(value).splitlines() or [""]
    return "\n".join(f"> {line}" for line in lines)


def render_triage_markdown(
    result: dict[str, Any] | None,
    metadata: dict[str, Any] | None,
    repository: str,
    run_id: str,
    server_url: str,
) -> str:
    source_url = run_url(server_url, repository, run_id)
    metadata = metadata or {}
    duration = metadata.get("duration_ms")
    duration_text = f"{float(duration) / 1000:.1f}s" if isinstance(duration, (int, float)) else "unknown"
    turns = safe_text(metadata.get("num_turns", "unknown"))
    cost = metadata.get("total_cost_usd")
    cost_text = f"${float(cost):.4f}" if isinstance(cost, (int, float)) else "unknown"
    denials = metadata.get("permission_denials")
    denial_count = len(denials) if isinstance(denials, list) else "unknown"

    if result is None:
        return (
            "## Claude E2E triage\n\n"
            "Claude Code did not produce a structured diagnosis. Inspect the live activity log and uploaded "
            f"progress artifact. [Source workflow run]({source_url})\n\n"
            f"| Turns | Duration | Cost | Permission denials |\n"
            f"| ---: | ---: | ---: | ---: |\n"
            f"| {turns} | {duration_text} | {cost_text} | {denial_count} |\n"
        )

    classification = safe_text(result.get("classification", "unknown"))
    confidence = safe_text(result.get("confidence", "unknown"))
    fix_applied = "yes" if result.get("fix_applied") is True else "no"
    return f"""## Claude E2E triage

| Classification | Confidence | Fix applied | Turns | Duration | Cost | Permission denials |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `{classification}` | {confidence} | {fix_applied} | {turns} | {duration_text} | {cost_text} | {denial_count} |

### Diagnosis

{quote(result.get("summary", "No summary reported."))}

### Evidence

{bullet_list(result.get("evidence"))}

### Reproduction

{quote(result.get("reproduction", "No reproduction reported."))}

### Proposed change

{quote(result.get("proposed_change", "No change proposed."))}

Changed files:

{bullet_list(result.get("changed_files"))}

### Verification

{bullet_list(result.get("verification"))}

### Recommended action

{quote(result.get("recommended_action", "No action reported."))}

[Source workflow run]({source_url}) · The uploaded `claude-progress.jsonl` contains the sanitized activity timeline.
"""


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else None


def github_escape(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--github-summary", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--server-url", required=True)
    args = parser.parse_args()

    result = load_json(args.result)
    metadata = load_json(args.metadata)
    markdown = render_triage_markdown(result, metadata, args.repository, args.run_id, args.server_url)
    with args.github_summary.open("a", encoding="utf-8") as summary:
        summary.write(markdown + "\n")

    if result is not None:
        classification = safe_text(result.get("classification", "unknown"))
        confidence = safe_text(result.get("confidence", "unknown"))
        diagnosis = github_escape(safe_text(result.get("summary", ""))[:500])
        print(f"::notice title=Claude triage: {classification} ({confidence})::{diagnosis}")


if __name__ == "__main__":
    main()
