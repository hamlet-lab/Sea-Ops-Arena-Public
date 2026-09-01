import json

from sea_ops_arena.demo import run_demo
from sea_ops_arena.reporting import to_json, to_markdown


def test_json_report_is_machine_readable() -> None:
    payload = json.loads(to_json(run_demo("balanced")))

    assert payload["suite_id"] == "public-demo-v1"
    assert payload["summary"]["total_cases"] == 3
    assert payload["summary"]["decision_match_rate"] == 1.0
    assert len(payload["cases"]) == 3


def test_markdown_report_marks_result_as_synthetic_example() -> None:
    report = to_markdown(run_demo("balanced"))

    assert "공개 합성 시나리오" in report
    assert "실제 제품 성능" in report
    assert "불필요 실행" in report
    assert "필요한 실행 누락" in report
