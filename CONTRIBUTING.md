# Contributing

This project is in blueprint stage. Keep changes small, testable, evidence-based, and safe for a local Ditto stack.

## Before Starting

- Open or create an issue using the relevant template; agree on module ownership and the acceptance criteria before parallel implementation.
- Check [the architecture](docs/architecture.md), [API contracts](docs/api-contracts.md), and the related decision records before changing a boundary.
- Never edit or commit the ignored `.local/ditto-upstream` checkout. Upstream behavior changes belong in a separate proposal to Eclipse Ditto, not a hidden local patch.

## Branches and Pull Requests

- Branch names: `feat/<issue>-short-name`, `fix/<issue>-short-name`, `docs/<issue>-short-name`, or `test/<issue>-short-name`.
- Keep a pull request focused on one contract or module. Include the issue reference, behavior change, tests/evidence, safety impact, and any schema/API version change.
- Require one teammate review, passing CI, and an explicit reviewer for changes to safety policy, fault execution, secrets, or public interfaces.
- Do not merge a change that enables fault injection by default, broadens a target allow-list without review, or lets model output execute commands.

## Module Ownership

Ownership is by role, not by named person. The team should assign one owner per role in its planning issue:

| Area | Suggested owner | Boundary |
| --- | --- | --- |
| Ditto adapter and discovery | Integration engineer | Read-only access to pinned deployment metadata and documented endpoints |
| Graph and contracts | Platform engineer | Versioned nodes, edges, provenance, and schemas |
| Telemetry and evaluation | Observability engineer | Baseline, windows, metric normalization, scoring inputs |
| Planner and AI analysis | AI engineer | Candidate ranking and evidence-grounded explanations; no execution capability |
| Safety and chaos adapter | Safety/chaos engineer | Fixed local target/action allow-list, approval checks, cleanup |
| Dashboard and report | UI engineer | Read-only presentation plus explicit approval interaction |
| Integration and demo | Test/integration owner | Repeatable setup, fixtures, end-to-end evidence, demo rehearsal |

One contributor may hold multiple roles, but the safety review should be independent of the author when team size permits.

## Conventions

- Python: type public functions, use small modules, and keep I/O at adapter boundaries.
- TypeScript (planned UI): strict mode and API types derived from versioned contracts; do not duplicate domain rules in the browser.
- JSON Schema is the source for exchanged records. Add a backward-compatible optional field or increment the contract version for incompatible changes; document migrations before changing stored data.
- Preserve metric name, labels, timestamp, unit, source, and confidence. Never claim correlation proves a causal edge.
- Use UTC timestamps. Keep test identifiers synthetic and use a dedicated Ditto namespace for load data.
- Do not store credentials, real customer data, unredacted logs, or private telemetry in fixtures or reports.

## Local Checks

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

For application changes, add focused tests and a documented local integration check. Fault-injection tests must use a disposable, isolated Ditto deployment and prove cleanup/recovery.