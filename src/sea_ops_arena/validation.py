from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .artifacts import sha256_file
from .contracts import DecisionStatus
from .public_results import load_public_decision_set
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


def validate_public_result_binding(
    suite_path: str | Path,
    decisions_path: str | Path,
) -> None:
    """엄격 공개 결과가 정확한 시나리오 파일과 결합되어 있는지 확인한다.

    단순 합성 fixture 파일에는 적용하지 않는다. 실제 모델·사람·외부 시스템에서
    기록된 엄격 공개 결과는 suite_sha256을 요구해, 다른 버전의 시나리오와
    실수로 섞여 평가되는 것을 막는다.
    """

    decisions_path = Path(decisions_path)
    raw = json.loads(decisions_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "schema_version" not in raw:
        return

    result_set = load_public_decision_set(decisions_path)
    if result_set.source.kind != "fixture" and result_set.suite_sha256 is None:
        raise ValueError(
            "fixture가 아닌 공개 결과에는 suite_sha256이 필요합니다"
        )

    if result_set.suite_sha256 is None:
        return

    actual_hash = sha256_file(suite_path)
    if result_set.suite_sha256 != actual_hash:
        raise ValueError(
            "공개 결과의 suite_sha256이 현재 시나리오 파일과 일치하지 않습니다"
        )
