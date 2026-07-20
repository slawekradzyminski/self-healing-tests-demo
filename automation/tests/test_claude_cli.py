from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from self_healing.claude_cli import (
    StreamObserver,
    describe_run,
    extract_structured_output,
    run_stream,
    sanitize_text,
    select_metadata,
)


class ClaudeCliTest(unittest.TestCase):
    def test_sanitizes_secret_assignments_and_token_values(self) -> None:
        text = sanitize_text("ANTHROPIC_API_KEY=secret ghp_abcdefghijklmnopqrstuvwxyz")

        self.assertEqual(text, "ANTHROPIC_API_KEY=[REDACTED] [REDACTED]")

    def test_observer_reports_notes_and_tools_but_omits_thinking(self) -> None:
        observer = StreamObserver()
        records = observer.observe(
            {
                "type": "assistant",
                "message": {
                    "content": [
                        {"type": "thinking", "thinking": "private"},
                        {"type": "text", "text": "The validation state is the key observation."},
                        {
                            "type": "tool_use",
                            "id": "tool-1",
                            "name": "Bash",
                            "input": {"command": "npm run test:e2e"},
                        },
                    ]
                },
            }
        )

        self.assertEqual([record["kind"] for record in records], ["note", "tool"])
        self.assertNotIn("private", json.dumps(records))
        self.assertIn("npm run test:e2e", str(records[1]["message"]))

        result = observer.observe(
            {
                "type": "user",
                "message": {
                    "content": [
                        {"type": "tool_result", "tool_use_id": "tool-1", "is_error": False}
                    ]
                },
            }
        )
        self.assertEqual(result[0]["message"], "Bash: completed")

    def test_stream_runner_writes_sanitized_progress_and_returns_result(self) -> None:
        final = {
            "type": "result",
            "subtype": "success",
            "num_turns": 3,
            "total_cost_usd": 0.2,
            "structured_output": {"classification": "TEST_DEFECT"},
        }
        stream = "\n".join(
            (
                json.dumps({"type": "system", "subtype": "init", "model": "opus", "tools": ["Bash"]}),
                json.dumps(
                    {
                        "type": "assistant",
                        "message": {
                            "content": [
                                {
                                    "type": "tool_use",
                                    "id": "tool-1",
                                    "name": "Bash",
                                    "input": {"command": "GH_TOKEN=secret npm test"},
                                }
                            ]
                        },
                    }
                ),
                json.dumps(final),
                "",
            )
        )
        process = Mock()
        process.stdout = io.StringIO(stream)
        process.wait.return_value = 0

        with tempfile.TemporaryDirectory() as directory, patch(
            "self_healing.claude_cli.subprocess.Popen", return_value=process
        ):
            progress_path = Path(directory) / "progress.jsonl"
            returncode, result = run_stream(["claude"], progress_path)
            progress = progress_path.read_text(encoding="utf-8")

        self.assertEqual(returncode, 0)
        self.assertEqual(result, final)
        self.assertIn("GH_TOKEN=[REDACTED] npm test", progress)
        self.assertNotIn("GH_TOKEN=secret", progress)

    def test_extracts_native_structured_output(self) -> None:
        expected = {"classification": "TEST_DEFECT"}

        self.assertEqual(extract_structured_output({"structured_output": expected}), expected)

    def test_extracts_json_result_for_compatible_cli_versions(self) -> None:
        expected = {"classification": "INCONCLUSIVE"}

        self.assertEqual(extract_structured_output({"result": '{"classification":"INCONCLUSIVE"}'}), expected)

    def test_rejects_unstructured_result(self) -> None:
        with self.assertRaisesRegex(ValueError, "structured JSON"):
            extract_structured_output({"result": "not JSON"})

    def test_metadata_excludes_session_and_result_content(self) -> None:
        metadata = select_metadata(
            {
                "num_turns": 12,
                "total_cost_usd": 0.42,
                "session_id": "secret-session",
                "result": "large result",
            }
        )

        self.assertEqual(metadata, {"num_turns": 12, "total_cost_usd": 0.42})

    def test_run_description_exposes_limits_without_result_content(self) -> None:
        description = describe_run(
            1,
            {
                "subtype": "error_max_turns",
                "is_error": True,
                "num_turns": 35,
                "total_cost_usd": 1.23,
            },
        )

        self.assertEqual(
            description,
            "Claude Code process: exit=1 subtype=error_max_turns is_error=True turns=35 cost_usd=1.23",
        )


if __name__ == "__main__":
    unittest.main()
