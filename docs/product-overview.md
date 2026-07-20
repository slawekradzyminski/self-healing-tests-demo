# Product overview

## Product

Awesome Testing is a public training application for realistic test-automation exercises. The tested commerce frontend exposes authentication, registration, products, carts, checkout, profiles, admin workflows, monitoring, email, QR, and AI-assisted testing screens.

The demo suite currently covers only public authentication behavior so that its green baseline requires no user or administrator credentials.

## Runtime topology

The public URL is served through a gateway. The gateway routes browser traffic to the frontend and API traffic to the backend. The local orchestration repository can start equivalent lightweight, full, and server profiles.

Primary components:

- `awesome-localstack`: Docker Compose profiles, gateway routing, deployment compatibility, and image pins.
- `vite-react-frontend`: React commerce frontend and browser-visible behavior.
- `test-secure-backend`: authentication, commerce APIs, persistence, and backend validation.
- `playwright-multiagent-demo`: reference Playwright architecture and the source patterns used by this demo.

## Public authentication behavior

- `/login` renders username and password inputs, a sign-in action, password recovery, and registration navigation.
- Submitting an empty required field produces client-side validation and should not authenticate.
- Invalid credentials keep the user on `/login` and show an error notification.
- Registration navigation opens `/register`.
- Submitting an empty registration form shows required-field validation without creating a user.

## Diagnostic ownership hints

- Browser layout, locators, client-side validation, and routing usually belong to `vite-react-frontend`.
- Authentication responses, API validation, and persistence usually belong to `test-secure-backend`.
- gateway reachability, container startup, public routing, and image compatibility usually belong to `awesome-localstack`.
- Playwright fixtures, page objects, assertions, retries, and test data belong to this repository.

These hints are not proof. The triage agent must use test artifacts, source inspection, and reproduction evidence before assigning a classification.
