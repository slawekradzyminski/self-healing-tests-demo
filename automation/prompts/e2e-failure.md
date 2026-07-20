Diagnose the failed Playwright E2E run in this repository and converge once the evidence is sufficient.

Investigation order:

1. Read `CLAUDE.md`, `docs/product-overview.md`, `docs/triage-contract.md`, `triage/source-repositories.json`, `test-output.log`, `test-results/results.json`, the failed test, and its page object.
2. Inspect relevant artifacts and the most likely source checkout under `.triage-sources`. Do not inspect unrelated repositories after ownership is established.
3. Re-run only the failed test with retries disabled.
4. Use `npx --no-install playwright-cli` for one focused live-browser investigation when reproduction is possible. Keep it headless and close the session.
5. Classify the failure. If and only if evidence demonstrates a `TEST_DEFECT` in this repository with confidence of at least 0.90, edit the smallest existing test-support source file and run both the focused test and `npm run test:e2e`.

Preserve business intent. Never skip a test, weaken an assertion, blindly update a snapshot, create files, modify product source, or edit workflow, policy, prompt, schema, or documentation files. Do not commit or push; a separate policy-enforcing publisher owns delivery.

For `PRODUCT_BUG`, `CI_ENVIRONMENT`, or `INCONCLUSIVE`, do not edit. Return `INCONCLUSIVE` when evidence cannot support another class.
