# Public Boundary

This repository is a public evaluation surface. It must remain useful without exposing the internals of any proprietary controller.

## 1. Boundary rule

Public code may describe **inputs, outputs, scenarios, simulator behavior, and scoring**.

Public code must not describe **how a proprietary controller internally reasons, represents state, evaluates policy, resolves authority, performs admission, or commits changes**.

The stable public seam is:

```text
ExecutionRequest -> ControllerAdapter -> DecisionReceipt
```

Everything behind `ControllerAdapter` is opaque unless it is an independently public implementation contributed specifically for demonstration purposes.

## 2. Allowed public material

The following categories are allowed when they are controller-agnostic:

- scenario fixtures and synthetic environments,
- benchmark metadata and versioning,
- model/agent output normalization,
- execution request schemas,
- decision receipt schemas,
- simulator state used only by the public benchmark,
- scoring functions whose publication does not reveal proprietary controller criteria,
- deterministic replay of public requests and receipts,
- reproducibility metadata,
- aggregate reports and benchmark results,
- adapters that call an external controller through a narrow documented interface.

## 3. Prohibited public material

Do not commit any of the following:

- proprietary controller source code,
- internal controller state schemas or state-transition logic,
- policy or governance implementations,
- internal gate/admission/commit logic,
- internal scoring or hidden evaluation criteria,
- proprietary rule tables or policy files,
- private architecture diagrams or composition documents,
- internal code names, unpublished component names, or internal filenames,
- private research notes, patent drafting material, invention notebooks, or claim mappings,
- production credentials, endpoints, infrastructure details, traces, prompts, or raw customer data,
- redaction deny-lists that enumerate confidential names or files,
- tests whose assertions disclose confidential invariants,
- comments or commit messages that explain confidential implementation choices,
- copied Git history, commits, trees, patches, or blobs from a private development repository.

## 4. Semantic review beats string review

A file can leak proprietary information even if it contains none of the forbidden names.

Before publication, review whether a technically competent reader could infer any proprietary controller mechanism by combining:

- type names,
- schemas,
- test invariants,
- examples,
- state transitions,
- policy tables,
- diagrams,
- error messages,
- benchmark categories,
- commit history.

A literal secret scan is necessary but not sufficient.

## 5. Controller adapters

A public adapter should do only what is required to transport a request and receive a receipt.

It may expose:

- protocol version,
- request identifier,
- public request payload,
- public decision status,
- public reason code,
- optional human-readable explanation,
- optional receipt integrity/provenance metadata.

It must not expose:

- internal state snapshots,
- internal policy identifiers,
- rule evaluation traces,
- hidden scores,
- internal branch or rollback data,
- intermediate reasoning,
- proprietary component topology.

## 6. Public simulator independence

The simulator in this repository is benchmark infrastructure. Its state model must be designed for the scenario itself and must not mirror a proprietary controller's internal state model.

Similarity of purpose is not enough to justify copying internal structures.

## 7. Publication workflow

For every change intended for `main`:

1. Build or edit only inside this public repository.
2. Do not cherry-pick, merge, import, or copy Git objects from a private repository.
3. Run secret and credential scans.
4. Run internal-name scans using a deny-list stored outside this repository.
5. Perform semantic IP review against this document.
6. Inspect the complete diff, including tests, fixtures, comments, documentation, and commit messages.
7. Publish only after the public surface can stand on its own without explaining proprietary internals.

## 8. Default decision

When uncertain whether a detail belongs here, omit it from the public repository and keep the boundary narrower.

The Arena should be inspectable. A proprietary controller does not need to be.
