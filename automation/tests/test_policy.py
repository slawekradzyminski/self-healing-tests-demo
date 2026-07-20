from __future__ import annotations

import unittest

from self_healing.policy import TriageResult, validate_changed_files


def result(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "classification": "TEST_DEFECT",
        "confidence": 0.98,
        "affected_repository": "owner/tests",
        "fix_applied": True,
        "changed_files": ["pages/LoginPage.ts"],
    }
    value.update(overrides)
    return value


class PolicyTest(unittest.TestCase):
    def test_high_confidence_local_test_defect_passes_gate(self) -> None:
        triage = TriageResult.from_dict(result())
        self.assertTrue(triage.satisfies_repair_gate("owner/tests"))

    def test_product_bug_never_passes_gate(self) -> None:
        triage = TriageResult.from_dict(result(classification="PRODUCT_BUG"))
        self.assertFalse(triage.satisfies_repair_gate("owner/tests"))

    def test_low_confidence_never_passes_gate(self) -> None:
        triage = TriageResult.from_dict(result(confidence=0.89))
        self.assertFalse(triage.satisfies_repair_gate("owner/tests"))

    def test_reported_and_actual_files_must_match(self) -> None:
        with self.assertRaisesRegex(ValueError, "do not match"):
            validate_changed_files(["pages/LoginPage.ts"], ["pages/RegisterPage.ts"])

    def test_workflow_changes_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "disallowed path"):
            validate_changed_files([".github/workflows/e2e.yml"], [".github/workflows/e2e.yml"])

    def test_allowed_typescript_change_is_returned(self) -> None:
        self.assertEqual(
            validate_changed_files(["pages/LoginPage.ts"], ["pages/LoginPage.ts"]),
            ("pages/LoginPage.ts",),
        )


if __name__ == "__main__":
    unittest.main()
