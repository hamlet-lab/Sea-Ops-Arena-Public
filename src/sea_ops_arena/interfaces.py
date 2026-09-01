from __future__ import annotations

from typing import Protocol

from .contracts import DecisionReceipt, ExecutionRequest, ExecutionResult


class ControllerAdapter(Protocol):
    """외부 의사결정 시스템과 연결하기 위한 최소 공개 인터페이스."""

    def evaluate(self, request: ExecutionRequest) -> DecisionReceipt:
        ...


class EnvironmentAdapter(Protocol):
    """공개 벤치마크 환경과 연결하기 위한 인터페이스."""

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        ...
