from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DecisionStatus(str, Enum):
    """Public controller outcome. No internal decision process is implied."""

    PROCEED = "proceed"
    REJECT = "reject"
    DEFER = "defer"


class ExecutionStatus(str, Enum):
    EXECUTED = "executed"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass(frozen=True)
class ExecutionRequest:
    """Controller-agnostic request emitted by an Arena adapter."""

    request_id: str
    scenario_id: str
    action: str
    target: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    context_refs: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionReceipt:
    """Opaque controller response exposed to the public Arena."""

    decision_id: str
    request_id: str
    status: DecisionStatus
    reason_code: str | None = None
    message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionResult:
    """Result reported by the public benchmark environment."""

    request_id: str
    status: ExecutionStatus
    result_ref: str | None = None
    message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
