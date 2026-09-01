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
    """Runs one public benchmark turn across the request/receipt boundary."""

    def __init__(self, controller: ControllerAdapter, environment: EnvironmentAdapter) -> None:
        self._controller = controller
        self._environment = environment

    def run(self, request: ExecutionRequest) -> ArenaTurn:
        receipt = self._controller.evaluate(request)

        if receipt.request_id != request.request_id:
            raise ValueError("controller receipt does not match request")

        if receipt.status is DecisionStatus.PROCEED:
            result = self._environment.execute(request)
            if result.request_id != request.request_id:
                raise ValueError("environment result does not match request")
        else:
            result = ExecutionResult(
                request_id=request.request_id,
                status=ExecutionStatus.SKIPPED,
                message="not executed by public harness",
            )

        return ArenaTurn(request=request, receipt=receipt, result=result)
