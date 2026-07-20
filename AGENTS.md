# Self-healing tests demo contributor guide

Use English for source code, documentation, test output, CI reports, and commit messages.

For UI tests:
- run newly created tests first and then full suite via `npm run test:ui`
- prefer `data-testid` selectors
- use given (test setup) / when(tested action) / then (assertions)
- use page object model, add pages to `/pages`, add components to `/components`. inject components in pages
- use Playwright CLI skill from the repo to explore the tested page first

For failure triage:
- diagnosis is read-only in the first iteration; do not edit tests or product sources
- classify failures according to `docs/triage-contract.md`
- verify claims with artifacts, source inspection, or a controlled reproduction
- never weaken, delete, skip, or rewrite an assertion merely to make a failure disappear
- return `INCONCLUSIVE` when the available evidence does not justify a stronger classification
