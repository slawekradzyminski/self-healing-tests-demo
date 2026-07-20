from __future__ import annotations

import unittest

from self_healing.claude_cli import describe_run, extract_structured_output, select_metadata


class ClaudeCliTest(unittest.TestCase):
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
