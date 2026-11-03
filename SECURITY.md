# Security Policy

## Reporting a vulnerability or a leak

Please **do not open a public issue** for:
- a security vulnerability in the repository tooling, starter code or GitHub workflows;
- committed secrets (API keys, tokens, passwords);
- personal data that should not be here;
- leaked **confidential assessor material** (reference solutions, hidden tests, marking guides).

Use GitHub's **private vulnerability reporting** for this repository (*Security → Report a vulnerability*), or contact the Intelligence Track lead directly. You'll get an acknowledgement within 5 working days.

## What we do

- **Secrets:** revoke them immediately, remove them from history where possible, and record the incident.
- **Personal data:** remove it, assess the incident under the Nigeria Data Protection Act 2023, and inform the affected people where required.
- **Leaked assessment material:** rotate or retire the affected assessments (see [maintenance §5](docs/contributing/maintenance.md#5-when-confidential-material-leaks)).

## Rules for contributors

- Never commit credentials. Use environment variables and a `.env.example` with dummy values.
- Never commit real personal data. Use synthetic data generators (see the [authoring guide](docs/contributing/AUTHORING_GUIDE.md#63-data-generators)).
- Starter code that runs untrusted model output or tool calls must sandbox it, and must document the trust boundary.
- GitHub Actions workflows use read-only permissions by default, and never expose secrets to pull requests from forks.
