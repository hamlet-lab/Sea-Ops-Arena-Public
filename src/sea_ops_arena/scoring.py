from __future__ import annotations

from dataclasses import dataclass

from .contracts import DecisionStatus, ExecutionStatus
from .scenarios import BenchmarkCase
from .runner import ArenaTurn


@dataclass(frozen=True)
class CaseScore:
    case_id: str
    decision_match: bool
    expected_proceed: bool
    actual_proceed: bool
    environment_success: bool | None


@dataclass(frozen=True)
class ScoreSummary:
    total_cases: int
    decision_matches: int
    decision_match_rate: float
    unnecessary_executions: int
    missed_executions: int
    successful_executions: int
    attempted_executions: int

    @property
    def execution_success_rate(self) -> float | None:
        if self.attempted_executions == 0:
            return None
        return self.successful_executions / self.attempted_executions


def score_case(case: BenchmarkCase, turn: ArenaTurn) -> CaseScore:
    expected_proceed = case.expected_decision is DecisionStatus.PROCEED
    actual_proceed = turn.receipt.status is DecisionStatus.PROCEED

    environment_success: bool | None = None
    if turn.result.status is not ExecutionStatus.SKIPPED:
        environment_success = turn.result.status is case.environment_status

    return CaseScore(
        case_id=case.case_id,
        decision_match=turn.receipt.status is case.expected_decision,
        expected_proceed=expected_proceed,
        actual_proceed=actual_proceed,
        environment_success=environment_success,
    )


def summarize(scores: list[CaseScore]) -> ScoreSummary:
    total = len(scores)
    matches = sum(score.decision_match for score in scores)
    unnecessary = sum(
        score.actual_proceed and not score.expected_proceed for score in scores
    )
    missed = sum(
        score.expected_proceed and not score.actual_proceed for score in scores
    )
    attempted = sum(score.environment_success is not None for score in scores)
    successful = sum(score.environment_success is True for score in scores)

    return ScoreSummary(
        total_cases=total,
        decision_matches=matches,
        decision_match_rate=(matches / total) if total else 0.0,
        unnecessary_executions=unnecessary,
        missed_executions=missed,
        successful_executions=successful,
        attempted_executions=attempted,
    )
