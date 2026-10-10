# Security Policy

## Scope

This repository is currently a blueprint and contract scaffold; there is no deployed orchestration service or fault runner to report against yet. Security reports about Eclipse Ditto itself must go to the [Eclipse Foundation security team](https://eclipse.org/security), not this project.

## Reporting

For a vulnerability in this project, use GitHub's private vulnerability reporting or Security Advisories when enabled. Do not file exploitable details, credentials, customer data, or private logs in a public issue. If private reporting is unavailable, contact the maintainers through the hackathon organizer and provide only the minimum reproduction details needed.

## Operational Safety

- Only test an isolated local deployment under your control. Never target public, shared, customer, or production systems.
- The planned runner must be disabled by default, require a human approval, and accept only named actions and allow-listed services.
- Keep Docker and Ditto ports on loopback. The Docker socket grants powerful host control; it must never be mounted into a public-facing API or LLM process.
- Treat Ditto DevOps APIs and credentials as privileged. Keep local credentials outside Git, rotate sample credentials, and never enable remote DevOps access for the demo.
- Do not commit `.env`, tokens, private certificates, raw customer data, or sensitive logs. Enable GitHub secret scanning and push protection on the eventual public repository where available.
- Keep dependency scanning and report upstream security findings with package/version/evidence; do not presume Ditto is vulnerable because it is used as a target.

## Licensing and Publication

The repository's original work is licensed under MIT, subject to confirmation of Bosch hackathon/employer IP rules. Eclipse Ditto is EPL-2.0 and remains a separate external dependency. Preserve its license, notices, and attribution when redistributing any Ditto artifacts. This repository has not been published.