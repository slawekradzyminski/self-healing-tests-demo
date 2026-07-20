from __future__ import annotations

import unittest

from self_healing.config import MAX_TURNS, load_prompt, load_schema, render_claude_args


class ConfigTest(unittest.TestCase):
    def test_configuration_is_renderable(self) -> None:
        self.assertEqual(MAX_TURNS, 35)
        self.assertIn("Diagnose the failed Playwright", load_prompt())
        self.assertIn("classification", load_schema()["required"])

        arguments = render_claude_args()
        self.assertIn("--max-turns 35", arguments)
        self.assertIn("--permission-mode bypassPermissions", arguments)
        self.assertIn("--dangerously-skip-permissions", arguments)
        self.assertNotIn("--allowedTools", arguments)


if __name__ == "__main__":
    unittest.main()
