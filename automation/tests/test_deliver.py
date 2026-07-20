from __future__ import annotations

import unittest

from self_healing.deliver import repair_branch, validate_branch


class DeliverTest(unittest.TestCase):
    def test_repair_branch_is_run_scoped(self) -> None:
        self.assertEqual(repair_branch("12345"), "claude/e2e-repair-12345")

    def test_main_is_never_a_delivery_target(self) -> None:
        with self.assertRaisesRegex(ValueError, "never pushes directly to main"):
            validate_branch("main")

    def test_existing_pr_branch_is_allowed(self) -> None:
        self.assertEqual(validate_branch("codex/fix-login"), "codex/fix-login")

    def test_unsafe_branch_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsafe branch"):
            validate_branch("../main")


if __name__ == "__main__":
    unittest.main()
