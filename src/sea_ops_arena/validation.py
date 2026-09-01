from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .artifacts import sha256_file
from .contracts import DecisionStatus
from .input_packs import load_input_pack
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
    input_pack_path: str | Path | None = None,
) -> None:
    """엄격 공개 결과가 정확한 평가 시나리오와 모델 입력팩에 결합됐는지 확인한다.

    단순 합성 fixture에는 입력팩 결합을 요구하지 않는다. 실제 모델·사람·외부
    시스템 결과는 평가용 시나리오 해시와 정답 비노출 입력팩 해시를 모두 요구한다.
    """

    suite_path = Path(suite_path)
    decisions_path = Path(decisions_path)
    raw = json.loads(decisions_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "schema_version" not in raw:
        return

    result_set = load_public_decision_set(decisions_path)
    is_fixture = result_set.source.kind == "fixture"

    if not is_fixture and result_set.suite_sha256 is None:
        raise ValueError("fixture가 아닌 공개 결과에는 suite_sha256이 필요합니다")

    actual_suite_hash = sha256_file(suite_path)
    if result_set.suite_sha256 is not None and result_set.suite_sha256 != actual_suite_hash:
        raise ValueError(
            "공개 결과의 suite_sha256이 현재 시나리오 파일과 일치하지 않습니다"
        )

    if is_fixture:
        return

    if result_set.input_pack_sha256 is None:
        raise ValueError(
            "fixture가 아닌 공개 결과에는 input_pack_sha256이 필요합니다"
        )
    if input_pack_path is None:
        raise ValueError(
            "fixture가 아닌 공개 결과를 평가하려면 --input-pack으로 모델 입력팩 파일을 제공해야 합니다"
        )

    input_pack_path = Path(input_pack_path)
    input_pack = load_input_pack(input_pack_path)
    source_suite = input_pack["source_suite"]
    if source_suite["sha256"] != actual_suite_hash:
        raise ValueError(
            "모델 입력팩의 source_suite.sha256이 현재 시나리오 파일과 일치하지 않습니다"
        )

    actual_input_hash = sha256_file(input_pack_path)
    if result_set.input_pack_sha256 != actual_input_hash:
        raise ValueError(
            "공개 결과의 input_pack_sha256이 제공된 모델 입력팩과 일치하지 않습니다"
        )
