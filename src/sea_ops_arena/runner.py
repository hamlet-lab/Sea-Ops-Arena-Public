from __future__ import annotations

from dataclasses import dataclass

from .contracts import DecisionReceipt, DecisionStatus, ExecutionRequest, ExecutionResult, ExecutionStatus
from .interfaces import ControllerAdapter, EnvironmentAdapter


@dataclass(frozen=True)
class ArenaTurn:
    request: ExecutionRequest
    receipt: DecisionReceipt
    result: ExecutionResult


class ArenaRunner:
    """공개 요청/결과 경계를 기준으로 벤치마크 한 회차를 실행한다."""

    def __init__(self, controller: ControllerAdapter, environment: EnvironmentAdapter) -> None:
        self._controller = controller
        self._environment = environment

    def run(self, request: ExecutionRequest) -> ArenaTurn:
        receipt = self._controller.evaluate(request)

        if receipt.request_id != request.request_id:
            raise ValueError("판단 결과의 요청 ID가 원래 요청과 일치하지 않습니다")

        if receipt.status is DecisionStatus.PROCEED:
            result = self._environment.execute(request)
            if result.request_id != request.request_id:
                raise ValueError("실행 결과의 요청 ID가 원래 요청과 일치하지 않습니다")
        else:
            result = ExecutionResult(
                request_id=request.request_id,
                status=ExecutionStatus.SKIPPED,
                message="공개 하네스에서 실행되지 않았습니다",
            )

        return ArenaTurn(request=request, receipt=receipt, result=result)
