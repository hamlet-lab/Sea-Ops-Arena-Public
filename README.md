# SEA Ops Arena

SEA Ops Arena is a public benchmark and evaluation harness for testing whether AI-generated operational proposals remain safe when they interact with a simulated or controlled environment.

This repository contains the **Arena**, not the implementation of SEA.

## What is public here

The public surface is intentionally small:

- scenario and benchmark formats,
- model-output adapters,
- a generic controller interface,
- public decision receipts,
- simulator-facing execution results,
- scoring and reproducibility utilities.

A controller may be local, remote, human-operated, rule-based, or proprietary. The Arena does not need to know how a controller reaches its decision.

```text
Model / Agent
     |
     v
Execution Request
     |
     v
Controller Adapter  <---- opaque boundary
     |
     v
Decision Receipt
     |
     v
Public Simulator
     |
     v
Score / Evidence Bundle
```

## What is deliberately not public

This repository does **not** publish proprietary controller internals, internal state representations, policy logic, governance logic, hidden evaluation criteria, private architecture documents, research artifacts, or production integration details.

The public contract ends at the request/receipt boundary.

See [`docs/PUBLIC_BOUNDARY.md`](docs/PUBLIC_BOUNDARY.md) before adding code or documentation.

## Repository status

This repository starts from a new Git history and is maintained as a public-only codebase. It does not inherit the history of any private development repository.

## Intended use

SEA Ops Arena is intended for reproducible evaluation of operational AI behavior. Public benchmark code should make experiments inspectable without making a proprietary decision system inspectable.

## Security and disclosure

Do not report or submit suspected proprietary implementation details through a public issue. See [`SECURITY.md`](SECURITY.md).
