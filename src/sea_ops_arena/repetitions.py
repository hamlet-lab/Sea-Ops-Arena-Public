from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from statistics import mean

from .benchmark import BenchmarkRun, run_suite
from .fixtures import ScriptedController, SyntheticEnvironment
from .io import load_suite
from .public_results import PublicDecisionSet, load_public_decision_set
from .validation import validate_decision_coverage, validate_public_result_binding


@dataclass(frozen=True)
class RepeatRun:
    source_file: str
    repeat_id: str
    result_set: PublicDecisionSet
    run: BenchmarkRun


@dataclass(frozen=True)
class RepeatSummary:
    label: str
    source_kind: str
    model_name: str | None
    model_version: str | None
    repeat_count: int
    total_cases: int
    stable_cases: int
    stability_rate: float
    decision_match_rate_mean: float
    decision_match_rate_min: float
    decision_match_rate_max: float
    unnecessary_executions_mean: float
    missed_executions_mean: float


@dataclass(frozen=True)
class RepeatEvaluation:
    runs: tuple[RepeatRun, ...]
    summary: RepeatSummary


def evaluate_repeated_results(
    suite_path: str | Path,
    result_paths: list[str | Path],
) -> RepeatEvaluation:
    """동일 출처의 엄격 공개 결과를 반복 실행 단위로 평가한다.

    원본 프롬프트나 내부 로그가 아니라 공개 최종 판단의 반복 변동만 계산한다.
    """

    if len(result_paths) < 2:
        raise ValueError("반복 평가는 둘 이상의 공개 결과 파일이 필요합니다")

    suite = load_suite(suite_path)
    environment_outcomes = {
        case.request.request_id: case.environment_status for case in suite.cases
    }
    runs: list[RepeatRun] = []
    identity: tuple[str, str, str | None, str | None] | None = None
    seen_repeat_ids: set[str] = set()

    for raw_path in result_paths:
        path = Path(raw_path)
        validate_public_result_binding(suite_path, path)
        result_set = load_public_decision_set(path)
        validate_decision_coverage(suite, result_set.decisions)

        repeat_id = result_set.source.repeat_id
        if repeat_id is None:
            raise ValueError("반복 평가용 공개 결과에는 source.repeat_id가 필요합니다")
        if repeat_id in seen_repeat_ids:
            raise ValueError(f"중복 repeat_id: {repeat_id}")
        seen_repeat_ids.add(repeat_id)

        current_identity = (
            result_set.label,
            result_set.source.kind,
            result_set.source.model_name,
            result_set.source.model_version,
        )
        if identity is None:
            identity = current_identity
        elif current_identity != identity:
            raise ValueError(
                "반복 평가 파일의 label/source/model 정보가 서로 일치하지 않습니다"
            )

        environment = SyntheticEnvironment(outcomes=dict(environment_outcomes))
        run = run_suite(suite, ScriptedController(result_set.decisions), environment)
        runs.append(
            RepeatRun(
                source_file=path.name,
                repeat_id=repeat_id,
                result_set=result_set,
                run=run,
            )
        )

    assert identity is not None

    stable_cases = 0
    for case in suite.cases:
        request_id = case.request.request_id
        observed = {run.result_set.decisions[request_id] for run in runs}
        if len(observed) == 1:
            stable_cases += 1

    match_rates = [run.run.summary.decision_match_rate for run in runs]
    unnecessary = [run.run.summary.unnecessary_executions for run in runs]
    missed = [run.run.summary.missed_executions for run in runs]
    total_cases = len(suite.cases)

    return RepeatEvaluation(
        runs=tuple(runs),
        summary=RepeatSummary(
            label=identity[0],
            source_kind=identity[1],
            model_name=identity[2],
            model_version=identity[3],
            repeat_count=len(runs),
            total_cases=total_cases,
            stable_cases=stable_cases,
            stability_rate=(stable_cases / total_cases) if total_cases else 0.0,
            decision_match_rate_mean=mean(match_rates),
            decision_match_rate_min=min(match_rates),
            decision_match_rate_max=max(match_rates),
            unnecessary_executions_mean=mean(unnecessary),
            missed_executions_mean=mean(missed),
        ),
    )


def repeat_evaluation_to_markdown(evaluation: RepeatEvaluation) -> str:
    """반복 결과와 변동성을 한국어 Markdown으로 출력한다."""

    summary = evaluation.summary
    model_text = summary.model_name or "-"
    if summary.model_version:
        model_text += f" ({summary.model_version})"

    lines = [
        "# SEA Ops Arena 반복 평가",
        "",
        f"- 결과 묶음: **{summary.label}**",
        f"- 출처 유형: `{summary.source_kind}`",
        f"- 모델: {model_text}",
        f"- 반복 횟수: **{summary.repeat_count}회**",
        "",
        "## 반복별 결과",
        "",
        "| 반복 | 판단 일치율 | 불필요 실행 | 필요한 실행 누락 |",
        "|---|---:|---:|---:|",
    ]

    for item in evaluation.runs:
        run_summary = item.run.summary
        lines.append(
            f"| `{item.repeat_id}` | {run_summary.decision_match_rate * 100:.1f}% | "
            f"{run_summary.unnecessary_executions} | {run_summary.missed_executions} |"
        )

    lines.extend(
        [
            "",
            "## 반복 안정성",
            "",
            f"- 판단 일치율 평균: **{summary.decision_match_rate_mean * 100:.1f}%**",
            f"- 판단 일치율 범위: **{summary.decision_match_rate_min * 100:.1f}% ~ {summary.decision_match_rate_max * 100:.1f}%**",
            f"- 모든 반복에서 동일한 판단을 낸 사례: **{summary.stable_cases}/{summary.total_cases}**",
            f"- 반복 판단 안정률: **{summary.stability_rate * 100:.1f}%**",
            f"- 평균 불필요 실행: **{summary.unnecessary_executions_mean:.2f}회**",
            f"- 평균 필요한 실행 누락: **{summary.missed_executions_mean:.2f}회**",
            "",
            "> 반복 판단 안정률은 공개된 최종 판단이 반복 간 동일했는지만 측정합니다. 내부 사고 과정이나 비공개 상태를 측정하지 않습니다.",
            "",
        ]
    )
    return "\n".join(lines)
