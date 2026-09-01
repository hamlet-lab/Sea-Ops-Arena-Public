from __future__ import annotations

import json

from .benchmark import BenchmarkRun


def run_to_dict(run: BenchmarkRun) -> dict[str, object]:
    summary = run.summary
    return {
        "suite_id": run.suite_id,
        "suite_title": run.suite_title,
        "summary": {
            "total_cases": summary.total_cases,
            "decision_matches": summary.decision_matches,
            "decision_match_rate": summary.decision_match_rate,
            "unnecessary_executions": summary.unnecessary_executions,
            "missed_executions": summary.missed_executions,
            "attempted_executions": summary.attempted_executions,
            "successful_executions": summary.successful_executions,
            "execution_success_rate": summary.execution_success_rate,
        },
        "cases": [
            {
                "case_id": record.case_id,
                "title": record.title,
                "decision": record.turn.receipt.status.value,
                "execution": record.turn.result.status.value,
                "decision_match": record.score.decision_match,
                "expected_proceed": record.score.expected_proceed,
                "actual_proceed": record.score.actual_proceed,
                "environment_success": record.score.environment_success,
            }
            for record in run.records
        ],
    }


def to_json(run: BenchmarkRun) -> str:
    """기계가 다시 읽을 수 있는 공개 JSON 결과를 만든다."""

    return json.dumps(run_to_dict(run), ensure_ascii=False, indent=2)


def to_markdown(run: BenchmarkRun) -> str:
    """외부 검토자가 빠르게 읽을 수 있는 한국어 Markdown 요약을 만든다."""

    summary = run.summary
    success_rate = (
        "실행 없음"
        if summary.execution_success_rate is None
        else f"{summary.execution_success_rate:.1%}"
    )

    lines = [
        f"# {run.suite_title} 결과",
        "",
        "> 이 보고서는 공개 합성 시나리오의 예시 실행 결과입니다. 실제 제품 성능이나 특정 AI 모델의 성능을 주장하지 않습니다.",
        "",
        "## 요약",
        "",
        f"- 전체 사례: **{summary.total_cases}개**",
        f"- 공개 정답과 판단 일치: **{summary.decision_matches}/{summary.total_cases} ({summary.decision_match_rate:.1%})**",
        f"- 불필요 실행: **{summary.unnecessary_executions}건**",
        f"- 필요한 실행 누락: **{summary.missed_executions}건**",
        f"- 시도된 실행의 성공률: **{success_rate}**",
        "",
        "## 사례별 결과",
        "",
        "| 사례 | 판단 | 실행 | 정답 일치 |",
        "|---|---|---|---|",
    ]

    for record in run.records:
        lines.append(
            "| "
            f"{record.title} | {record.turn.receipt.status.value} | "
            f"{record.turn.result.status.value} | "
            f"{'예' if record.score.decision_match else '아니오'} |"
        )

    lines.extend(
        [
            "",
            "## 해석 범위",
            "",
            "이 결과는 Arena의 공개 실행·집계 기능이 어떻게 동작하는지 보여주기 위한 합성 예시입니다. 연결된 외부 의사결정 시스템의 내부 구조나 판단 과정을 포함하지 않습니다.",
        ]
    )
    return "\n".join(lines) + "\n"
