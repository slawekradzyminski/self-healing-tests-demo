# Repair pull requests

## Recommended boundary

The current demonstration keeps classification and editing in one bounded Claude session so it can prove a test defect before editing. Claude has unrestricted tools inside an ephemeral GitHub-hosted runner, but that job receives only a read-only repository token. It can create a local patch artifact; it cannot publish code.

A separate deterministic job checks `TEST_DEFECT`, confidence of at least 0.90, repository ownership, exact changed-file agreement, allowed paths, TypeScript, and the smoke suite before committing. Its short-lived write token is not present while candidate commands execute. On PR failures it pushes only to the existing same-repository PR branch; on trusted `main` failures it opens a draft repair PR. The original run remains red and the repair commit starts a fresh CI run.

For a hardened production design, put the publisher behind a protected GitHub environment and require human approval before its write token is issued.

```mermaid
flowchart LR
    Failure["Failed E2E run"] --> Triage["Unrestricted local sandbox; read-only GitHub"]
    Triage --> Gate{"TEST_DEFECT and high confidence?"}
    Gate -->|No| Report["Report only"]
    Gate -->|Yes| Approval["Human or environment approval"]
    Approval --> Repair["Deterministic patch publisher"]
    Repair --> Verify["Focused rerun plus regression suite"]
    Verify --> Draft["Commit to existing PR branch"]
```

## Same-repository repair

A prototype that fixes tests in `self-healing-tests-demo` is moderate work. The current workflow separates the unrestricted Claude sandbox from the write-capable publisher. GitHub groups PR creation and merging under `pull-requests: write`, so there is no create-only token permission. The trusted delivery module contains only draft-PR creation and existing-PR branch update paths—no merge path. Repository rules should additionally require review and prevent direct pushes to `main`.

The key guard is semantic: the agent should first capture the actual product behavior with Playwright CLI, then modify the test, then show that the formerly failing scenario and the smoke suite pass. A PR should include the original classification, evidence, exact rerun commands, and links to artifacts.

## Cross-repository repair

Opening a fix in one of the product repositories is a larger step. The workflow's default `GITHUB_TOKEN` is scoped to this repository, so it cannot push branches to every cloned source. Prefer a GitHub App installed only on the approved repositories and mint a short-lived installation token in the repair job. A fine-grained personal access token is possible but has a broader human identity and is less attractive operationally.

Each repository also needs an explicit validation contract, for example frontend lint/build/tests, backend Gradle tests, or Compose validation. The source registry should eventually declare the default branch, permitted paths, and validation command. Multi-repository incidents should create separate linked draft PRs or stop at an issue when the change cannot be verified atomically.

## Safety controls

- Run repair only on trusted events; never expose write credentials to forked pull requests.
- Treat page content, test data, logs, and artifacts as untrusted input that may contain prompt injection.
- Keep the unrestricted agent inside an ephemeral runner with a read-only GitHub token; grant write access only to deterministic code.
- Require a clean checkout and reject changes outside the selected repository and permitted paths.
- Cap turns, cost, changed files, and diff size.
- Require focused reproduction before editing and independent tests after editing.
- Open a draft PR for human review; do not enable automatic merge.
- Keep product-bug and inconclusive results diagnosis-only until repository-specific repair policies exist.

## Effort estimate

- Same-repository test-fix prototype: roughly half a day to one day.
- Reviewable, guarded same-repository workflow: roughly one to two days.
- Cross-repository GitHub App permissions, validation contracts, and safe draft PR creation: roughly two to five days.
- Reliable autonomous product repair across coordinated repositories: a larger engineering project and not an appropriate first self-healing milestone.

The estimates assume the current triage result is already dependable. Improving classification quality and building representative failure fixtures should come before granting write access.
