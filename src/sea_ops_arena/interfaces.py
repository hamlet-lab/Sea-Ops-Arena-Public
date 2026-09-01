from __future__ import annotations

from typing import Protocol

from .contracts import DecisionReceipt, ExecutionRequest, ExecutionResult


class ControllerAdapter(Protocol):
    """Narrow public seam for any external decision system."""

    def evaluate(self, request: ExecutionRequest) -> DecisionReceipt:
        ...


class EnvironmentAdapter(Protocol):
    """Public benchmark environment interface."""

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        ...
