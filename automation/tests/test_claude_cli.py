from __future__ import annotations

import unittest

from self_healing.claude_cli import extract_structured_output, select_metadata


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


if __name__ == "__main__":
    unittest.main()
