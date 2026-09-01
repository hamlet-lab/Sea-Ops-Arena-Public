from __future__ import annotations

from dataclasses import dataclass, field

from .contracts import DecisionStatus, ExecutionRequest, ExecutionStatus


@dataclass(frozen=True)
class BenchmarkCase:
    """공개 벤치마크의 단일 사례.

    기대값은 이 합성 시나리오가 외부에 공개하는 정답표일 뿐이며,
    연결된 의사결정 시스템의 내부 기준을 의미하지 않는다.
    """

    case_id: str
    title: str
    description: str
    request: ExecutionRequest
    expected_decision: DecisionStatus
    environment_status: ExecutionStatus = ExecutionStatus.EXECUTED
    tags: tuple[str, ...] = ()
    notes: str | None = None


@dataclass(frozen=True)
class BenchmarkSuite:
    """동일한 공개 조건으로 반복 평가하기 위한 사례 묶음."""

    suite_id: str
    title: str
    description: str
    cases: tuple[BenchmarkCase, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)

    def case_ids(self) -> tuple[str, ...]:
        return tuple(case.case_id for case in self.cases)
