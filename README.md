# Self-Healing Tests Demo

This repository is a small, deliberately conservative demonstration of AI-assisted E2E failure triage.

The initial version does not modify tests. It establishes a trustworthy baseline:

1. The repository contains the Playwright suite from `playwright-multiagent-demo/wynik`.
2. CI runs a deterministic public-auth smoke profile derived from that suite against the Awesome Testing training application.
3. Playwright preserves logs, screenshots, videos, traces, and a JSON report.
4. Claude Code runs only when the E2E test step fails.
5. Product and reference-test repositories are cloned only on that failure path.
6. Claude investigates the failure with repository context and Playwright CLI, then returns structured triage.
7. The workflow keeps the original E2E result red.

## Current target

The default target is:

```text
https://aitesters.byst.re
```

Override it locally or in GitHub Actions with `APP_BASE_URL`.

The application is a public training playground. Tests must use fake data and must not assume persistent state.

## Run locally

```bash
npm ci
npx playwright install chromium
cp .env.example .env
# Replace the example administrator values in .env with the training credentials.
npm run test:e2e
```

The default command runs the credential-free smoke profile. The complete inherited suite is available with:

```bash
npm run test:all
```

The full suite creates users and products and requires administrator credentials. Against the shared public target it can also encounter environment rate limits, so it is intentionally not the first CI baseline.

Open the generated HTML report with:

```bash
npm run report
```

## Failure-only triage flow

```mermaid
flowchart LR
    E2E["Run Playwright E2E tests"]
    Pass["Pass: finish without Claude"]
    Evidence["Failure: retain evidence"]
    Sources["Clone declared source repositories"]
    Claude["Claude Code + Playwright CLI"]
    Result["Structured diagnosis"]
    Red["Preserve failed CI result"]

    E2E -->|green| Pass
    E2E -->|red| Evidence
    Evidence --> Sources
    Sources --> Claude
    Claude --> Result
    Result --> Red
```

The source registry is [`triage/source-repositories.json`](triage/source-repositories.json). The product description and diagnostic contract live in [`docs/product-overview.md`](docs/product-overview.md) and [`docs/triage-contract.md`](docs/triage-contract.md).

## GitHub configuration

The workflow expects one repository secret:

```text
ANTHROPIC_API_KEY
```

An optional repository variable overrides the target:

```text
APP_BASE_URL
```

`ADMIN_PASSWORD` and the non-sensitive administrator variables are needed only when the complete inherited suite is enabled in CI later.

For security, Claude triage is skipped for pull requests originating from forks because GitHub does not expose repository secrets to those runs.

## Roadmap

The next iterations can introduce controlled examples for each classification and, only after the diagnosis is reliable, an optional repair branch for high-confidence `TEST_DEFECT` results. Repairs should always be reviewed and must prove that the original business assertion remains intact.
