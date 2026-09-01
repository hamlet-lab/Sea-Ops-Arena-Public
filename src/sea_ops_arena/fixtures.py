from __future__ import annotations

from dataclasses import dataclass

from .contracts import DecisionReceipt, DecisionStatus, ExecutionRequest, ExecutionResult, ExecutionStatus


class ScriptedController:
    """예시 실행을 위한 고정 응답 컨트롤러.

    SEA 또는 다른 실제 의사결정 시스템을 흉내 내지 않는다.
    공개 예제에서 미리 준비된 판단 결과를 재생하는 데만 사용한다.
    """

    def __init__(self, decisions: dict[str, DecisionStatus]) -> None:
        self._decisions = dict(decisions)

    def evaluate(self, request: ExecutionRequest) -> DecisionReceipt:
        status = self._decisions.get(request.request_id, DecisionStatus.DEFER)
        return DecisionReceipt(
            decision_id=f"fixture-{request.request_id}",
            request_id=request.request_id,
            status=status,
            reason_code="public_fixture",
            message="공개 예시용 고정 판단 결과",
        )


@dataclass
class SyntheticEnvironment:
    """벤치마크 자체가 소유하는 단순 합성 실행 환경."""

    outcomes: dict[str, ExecutionStatus]

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        status = self.outcomes.get(request.request_id, ExecutionStatus.EXECUTED)
        return ExecutionResult(
            request_id=request.request_id,
            status=status,
            result_ref=f"synthetic-{request.request_id}",
            message="공개 합성 환경의 실행 결과",
        )
