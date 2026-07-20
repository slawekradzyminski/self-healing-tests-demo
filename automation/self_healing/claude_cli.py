from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
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
SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b([A-Z0-9_]*(?:KEY|TOKEN|PASSWORD|SECRET)[A-Z0-9_]*)\s*=\s*(?:\"[^\"]*\"|'[^']*'|\S+)"
)
SECRET_VALUE = re.compile(r"\b(?:sk-ant-|gh[oprsu]_)[A-Za-z0-9_-]+\b")


def sanitize_text(value: object, limit: int = 700) -> str:
    text = str(value).replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\n", " ; ")
    text = SECRET_ASSIGNMENT.sub(lambda match: f"{match.group(1)}=[REDACTED]", text)
    text = SECRET_VALUE.sub("[REDACTED]", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        return text[: limit - 1] + "…"
    return text


def summarize_tool_input(name: str, value: object) -> str:
    if not isinstance(value, dict):
        return ""

    preferred_fields = {
        "Bash": ("command", "description"),
        "Read": ("file_path",),
        "Edit": ("file_path",),
        "Write": ("file_path",),
        "Glob": ("pattern", "path"),
        "Grep": ("pattern", "path"),
        "WebFetch": ("url", "prompt"),
        "WebSearch": ("query",),
        "Task": ("description", "subagent_type"),
    }
    fields = preferred_fields.get(name, ())
    details = [sanitize_text(value[field], 500) for field in fields if value.get(field)]
    return " | ".join(details)


class StreamObserver:
    def __init__(self) -> None:
        self.started = time.monotonic()
        self.tools: dict[str, str] = {}

    def record(self, kind: str, message: str) -> dict[str, object]:
        return {
            "elapsed_seconds": round(time.monotonic() - self.started, 1),
            "kind": kind,
            "message": sanitize_text(message),
        }

    def observe(self, event: dict[str, Any]) -> list[dict[str, object]]:
        records: list[dict[str, object]] = []
        event_type = event.get("type")

        if event_type == "system" and event.get("subtype") == "init":
            model = event.get("model", "unknown")
            tools = event.get("tools")
            tool_count = len(tools) if isinstance(tools, list) else "unknown"
            records.append(self.record("session", f"started; model={model}; available_tools={tool_count}"))

        elif event_type == "assistant":
            message = event.get("message")
            content = message.get("content", []) if isinstance(message, dict) else []
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict):
                    continue
                block_type = block.get("type")
                if block_type == "text" and block.get("text"):
                    records.append(self.record("note", str(block["text"])))
                elif block_type == "tool_use":
                    name = sanitize_text(block.get("name", "unknown"), 100)
                    tool_id = block.get("id")
                    if isinstance(tool_id, str):
                        self.tools[tool_id] = name
                    detail = summarize_tool_input(name, block.get("input"))
                    records.append(self.record("tool", f"{name}: {detail}" if detail else name))
                # Intentionally omit thinking and signature blocks.

        elif event_type == "user":
            message = event.get("message")
            content = message.get("content", []) if isinstance(message, dict) else []
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict) or block.get("type") != "tool_result":
                    continue
                tool_id = block.get("tool_use_id")
                name = self.tools.get(tool_id, "tool") if isinstance(tool_id, str) else "tool"
                status = "failed" if block.get("is_error") else "completed"
                records.append(self.record("tool-result", f"{name}: {status}"))

        elif event_type == "rate_limit_event":
            records.append(self.record("rate-limit", "Claude API rate-limit status changed"))

        elif event_type == "result":
            records.append(
                self.record(
                    "result",
                    "completed; "
                    f"subtype={event.get('subtype', 'unknown')}; "
                    f"turns={event.get('num_turns', 'unknown')}; "
                    f"cost_usd={event.get('total_cost_usd', 'unknown')}",
                )
            )

        return records


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


def run_stream(command: list[str], progress_path: Path) -> tuple[int, dict[str, Any] | None]:
    observer = StreamObserver()
    final_payload: dict[str, Any] | None = None
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    if process.stdout is None:
        raise RuntimeError("Claude Code stdout was not available")

    try:
        with progress_path.open("w", encoding="utf-8") as progress:
            for line_number, line in enumerate(process.stdout, start=1):
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"Claude emitted invalid stream JSON on line {line_number}") from error
                if not isinstance(event, dict):
                    continue
                if event.get("type") == "result":
                    final_payload = event
                for record in observer.observe(event):
                    progress.write(json.dumps(record, ensure_ascii=False) + "\n")
                    progress.flush()
                    print(
                        f"[claude/{record['kind']} +{record['elapsed_seconds']}s] {record['message']}",
                        flush=True,
                    )
    except BaseException:
        process.terminate()
        process.wait()
        raise

    return process.wait(), final_payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--executable", default="claude")
    args = parser.parse_args()

    returncode, payload = run_stream(
        [args.executable, *claude_arguments(), load_prompt()],
        args.progress,
    )
    if payload is None:
        raise RuntimeError(f"Claude Code exited with status {returncode} and no result event")

    metadata = select_metadata(payload)
    args.metadata.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(describe_run(returncode, metadata), flush=True)

    if returncode != 0:
        raise RuntimeError(f"Claude Code exited with status {returncode}")

    structured = extract_structured_output(payload)
    args.result.write_text(json.dumps(structured, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
