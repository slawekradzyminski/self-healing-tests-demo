from __future__ import annotations

import unittest

from self_healing.report import render_triage_markdown, run_url


class ReportTest(unittest.TestCase):
    def test_run_url_is_repository_scoped(self) -> None:
        self.assertEqual(
            run_url("https://github.com", "owner/repo", "123"),
            "https://github.com/owner/repo/actions/runs/123",
        )

    def test_report_contains_decision_evidence_change_verification_and_metrics(self) -> None:
        markdown = render_triage_markdown(
            {
                "classification": "TEST_DEFECT",
                "confidence": 0.97,
                "fix_applied": True,
                "summary": "The page object waits for an event that cannot happen.",
                "evidence": ["The form reports client validation without a request."],
                "reproduction": "Focused test failed before the change.",
                "proposed_change": "Remove the impossible wait.",
                "changed_files": ["pages/LoginPage.ts"],
                "verification": ["4 smoke tests passed"],
                "recommended_action": "Review the draft PR.",
            },
            {
                "duration_ms": 201344,
                "num_turns": 19,
                "total_cost_usd": 1.083944,
                "permission_denials": [],
            },
            "owner/repo",
            "123",
            "https://github.com",
        )

        for expected in (
            "`TEST_DEFECT`",
            "0.97",
            "19",
            "$1.0839",
            "### Evidence",
            "### Proposed change",
            "pages/LoginPage.ts",
            "### Verification",
            "actions/runs/123",
        ):
            self.assertIn(expected, markdown)

    def test_report_neutralizes_mentions_and_html(self) -> None:
        markdown = render_triage_markdown(
            {
                "classification": "INCONCLUSIVE",
                "summary": "@team <script>alert(1)</script>",
            },
            None,
            "owner/repo",
            "123",
            "https://github.com",
        )

        self.assertNotIn("@team", markdown)
        self.assertNotIn("<script>", markdown)


if __name__ == "__main__":
    unittest.main()
