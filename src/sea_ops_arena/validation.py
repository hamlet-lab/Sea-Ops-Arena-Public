from __future__ import annotations

from dataclasses import dataclass

from .contracts import DecisionStatus
from .scenarios import BenchmarkSuite


@dataclass(frozen=True)
class DecisionCoverage:
    missing_request_ids: tuple[str, ...]
    unexpected_request_ids: tuple[str, ...]

    @property
    def is_complete(self) -> bool:
        return not self.missing_request_ids and not self.unexpected_request_ids


def inspect_decision_coverage(
    suite: BenchmarkSuite,
    decisions: dict[str, DecisionStatus],
) -> DecisionCoverage:
    """공개 시나리오와 판단 결과 파일의 요청 ID 대응 상태를 확인한다."""

    expected = {case.request.request_id for case in suite.cases}
    provided = set(decisions)
    return DecisionCoverage(
        missing_request_ids=tuple(sorted(expected - provided)),
        unexpected_request_ids=tuple(sorted(provided - expected)),
    )


def validate_decision_coverage(
    suite: BenchmarkSuite,
    decisions: dict[str, DecisionStatus],
) -> None:
    """누락 또는 불필요한 요청 ID가 있으면 실행 전에 명확한 오류를 낸다."""

    coverage = inspect_decision_coverage(suite, decisions)
    if coverage.is_complete:
        return

    parts: list[str] = []
    if coverage.missing_request_ids:
        parts.append("누락=" + ", ".join(coverage.missing_request_ids))
    if coverage.unexpected_request_ids:
        parts.append("예상하지 않은 ID=" + ", ".join(coverage.unexpected_request_ids))
    raise ValueError("판단 결과 파일의 요청 ID가 시나리오와 일치하지 않습니다: " + "; ".join(parts))
