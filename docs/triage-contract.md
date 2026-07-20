# Failure triage contract

## Classifications

### `PRODUCT_BUG`

The test intent is still valid and the product violates it. A live reproduction, trace, API response, console error, or source-level evidence should demonstrate the product behavior.

### `TEST_DEFECT`

The product satisfies the intended behavior, but the test has an obsolete locator, incorrect assertion, invalid setup, state leak, or another defect in test code.

### `CI_ENVIRONMENT`

The runner, browser installation, DNS, TLS, dependency installation, target availability, resource pressure, or CI configuration prevented meaningful evaluation of product behavior.

### `INCONCLUSIVE`

Evidence is missing, contradictory, intermittent, or insufficient to distinguish the other classifications.

## Required investigation

1. Read the failed test and its page object before reproducing it.
2. Read `test-output.log` and `test-results/results.json` when available.
3. Inspect screenshots, video, traces, browser console output, and failed requests when relevant.
4. Inspect the corresponding product source checkout under `.triage-sources`.
5. Re-run only the failed scenario first.
6. Use Playwright CLI to inspect the application through the same test setup when possible.
7. Do not mutate product sources. A test repair is permitted only after the evidence proves `TEST_DEFECT` in this repository with confidence of at least 0.90.
8. A repair must preserve the intended behavior and pass both a focused rerun and the smoke suite.

## Output fields

- `classification`: one of the four classifications above.
- `confidence`: number from 0 to 1.
- `summary`: concise explanation of the most likely cause.
- `evidence`: concrete observations with paths, commands, or browser/API outcomes.
- `reproduction`: whether and how the failure was reproduced.
- `recommended_action`: the smallest safe next action and likely owner.
- `affected_repository`: the repository most likely to contain the cause or `unknown`.
- `proposed_change`: the smallest safe change indicated by the evidence, whether applied automatically or left for review.
- `fix_applied`: whether Claude changed this repository after satisfying the repair gate.
- `changed_files`: files changed by the repair, otherwise an empty list.
- `verification`: focused and regression commands run after the repair, otherwise an empty list.
