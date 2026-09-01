from sea_ops_arena import (
    ArenaRunner,
    DecisionReceipt,
    DecisionStatus,
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
)


class StaticController:
    def __init__(self, status: DecisionStatus) -> None:
        self.status = status

    def evaluate(self, request: ExecutionRequest) -> DecisionReceipt:
        return DecisionReceipt(
            decision_id="decision-1",
            request_id=request.request_id,
            status=self.status,
        )


class RecordingEnvironment:
    def __init__(self) -> None:
        self.calls = 0

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        self.calls += 1
        return ExecutionResult(
            request_id=request.request_id,
            status=ExecutionStatus.EXECUTED,
            result_ref="result-1",
        )


def make_request() -> ExecutionRequest:
    return ExecutionRequest(
        request_id="request-1",
        scenario_id="scenario-1",
        action="example_action",
    )


def test_proceed_executes_environment() -> None:
    environment = RecordingEnvironment()
    turn = ArenaRunner(StaticController(DecisionStatus.PROCEED), environment).run(make_request())

    assert environment.calls == 1
    assert turn.result.status is ExecutionStatus.EXECUTED


def test_non_proceed_does_not_execute_environment() -> None:
    for status in (DecisionStatus.REJECT, DecisionStatus.DEFER):
        environment = RecordingEnvironment()
        turn = ArenaRunner(StaticController(status), environment).run(make_request())

        assert environment.calls == 0
        assert turn.result.status is ExecutionStatus.SKIPPED
