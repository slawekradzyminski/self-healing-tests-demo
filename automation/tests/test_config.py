from __future__ import annotations

import unittest

from self_healing.config import (
    CLAUDE_CODE_VERSION,
    MAX_BUDGET_USD,
    MAX_TURNS,
    claude_arguments,
    load_prompt,
    load_schema,
)


class ConfigTest(unittest.TestCase):
    def test_configuration_is_renderable(self) -> None:
        self.assertEqual(MAX_TURNS, 35)
        self.assertEqual(MAX_BUDGET_USD, 2.0)
        self.assertEqual(CLAUDE_CODE_VERSION, "2.1.158")
        self.assertIn("Diagnose the failed Playwright", load_prompt())
        self.assertIn("classification", load_schema()["required"])

        arguments = claude_arguments()
        self.assertEqual(arguments[arguments.index("--max-turns") + 1], "35")
        self.assertEqual(arguments[arguments.index("--max-budget-usd") + 1], "2.0")
        self.assertEqual(arguments[arguments.index("--permission-mode") + 1], "bypassPermissions")
        self.assertIn("--dangerously-skip-permissions", arguments)
        self.assertNotIn("--allowedTools", arguments)


if __name__ == "__main__":
    unittest.main()
