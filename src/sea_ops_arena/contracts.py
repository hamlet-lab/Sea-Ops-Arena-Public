from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DecisionStatus(str, Enum):
    """외부에 공개되는 판단 결과 상태. 내부 판단 과정은 이 값으로부터 추정할 수 없다."""

    PROCEED = "proceed"
    REJECT = "reject"
    DEFER = "defer"


class ExecutionStatus(str, Enum):
    EXECUTED = "executed"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass(frozen=True)
class ExecutionRequest:
    """Arena 어댑터가 생성하는, 특정 내부 구현에 종속되지 않은 실행 요청."""

    request_id: str
    scenario_id: str
    action: str
    target: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    context_refs: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionReceipt:
    """비공개 내부 구현을 노출하지 않고 Arena에 전달되는 공개 판단 결과."""

    decision_id: str
    request_id: str
    status: DecisionStatus
    reason_code: str | None = None
    message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionResult:
    """공개 벤치마크 환경이 보고하는 실행 결과."""

    request_id: str
    status: ExecutionStatus
    result_ref: str | None = None
    message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
