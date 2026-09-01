from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .benchmark import BenchmarkRun, run_suite
from .fixtures import ScriptedController, SyntheticEnvironment
from .io import load_decisions, load_suite
from .validation import validate_decision_coverage, validate_public_result_binding


@dataclass(frozen=True)
class ComparisonRow:
    label: str
    source_file: str
    run: BenchmarkRun


def compare_decision_files(
    suite_path: str | Path,
    decision_paths: list[str | Path],
    input_pack_path: str | Path | None = None,
) -> tuple[ComparisonRow, ...]:
    """같은 공개 시나리오에 여러 판단 결과 파일을 적용해 비교한다."""

    if len(decision_paths) < 2:
        raise ValueError("비교하려면 둘 이상의 판단 결과 파일이 필요합니다")

    suite = load_suite(suite_path)
    rows: list[ComparisonRow] = []

    for raw_path in decision_paths:
        path = Path(raw_path)
        validate_public_result_binding(suite_path, path, input_pack_path)
        decisions = load_decisions(path)
        validate_decision_coverage(suite, decisions)
        environment = SyntheticEnvironment(
            outcomes={case.request.request_id: case.environment_status for case in suite.cases}
        )
        run = run_suite(suite, ScriptedController(decisions), environment)
        rows.append(
            ComparisonRow(
                label=path.stem,
                source_file=path.name,
                run=run,
            )
        )

    return tuple(rows)


def comparison_to_markdown(rows: tuple[ComparisonRow, ...]) -> str:
    """종합 순위를 만들지 않고 공개 관찰값을 나란히 보여 준다."""

    if not rows:
        return "# 비교 결과\n\n비교 결과가 없습니다.\n"

    lines = [
        "# SEA Ops Arena 비교 결과",
        "",
        "아래 값은 동일한 공개 시나리오에 서로 다른 판단 결과 파일을 적용한 결과입니다.",
        "임의의 가중 종합점수나 순위는 만들지 않습니다.",
        "",
        "| 입력 | 판단 일치율 | 불필요 실행 | 필요한 실행 누락 | 실행 성공률 |",
        "|---|---:|---:|---:|---:|",
    ]

    for row in rows:
        summary = row.run.summary
        success_rate = summary.execution_success_rate
        success_text = "-" if success_rate is None else f"{success_rate * 100:.1f}%"
        lines.append(
            f"| `{row.source_file}` | {summary.decision_match_rate * 100:.1f}% | "
            f"{summary.unnecessary_executions} | {summary.missed_executions} | {success_text} |"
        )

    lines.extend(
        [
            "",
            "> 저장소에 포함된 기본 비교 파일은 합성 고정 예시이며 실제 모델 또는 SEA 성능이 아닙니다.",
            "",
        ]
    )
    return "\n".join(lines)
