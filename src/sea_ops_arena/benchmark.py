from __future__ import annotations

from dataclasses import dataclass

from .interfaces import ControllerAdapter, EnvironmentAdapter
from .runner import ArenaRunner, ArenaTurn
from .scenarios import BenchmarkSuite
from .scoring import CaseScore, ScoreSummary, score_case, summarize


@dataclass(frozen=True)
class BenchmarkRecord:
    case_id: str
    title: str
    turn: ArenaTurn
    score: CaseScore


@dataclass(frozen=True)
class BenchmarkRun:
    suite_id: str
    suite_title: str
    records: tuple[BenchmarkRecord, ...]
    summary: ScoreSummary


def run_suite(
    suite: BenchmarkSuite,
    controller: ControllerAdapter,
    environment: EnvironmentAdapter,
) -> BenchmarkRun:
    """공개 시나리오 묶음을 동일한 인터페이스로 순차 실행한다."""

    runner = ArenaRunner(controller, environment)
    records: list[BenchmarkRecord] = []
    scores: list[CaseScore] = []

    for case in suite.cases:
        turn = runner.run(case.request)
        score = score_case(case, turn)
        scores.append(score)
        records.append(
            BenchmarkRecord(
                case_id=case.case_id,
                title=case.title,
                turn=turn,
                score=score,
            )
        )

    return BenchmarkRun(
        suite_id=suite.suite_id,
        suite_title=suite.title,
        records=tuple(records),
        summary=summarize(scores),
    )
