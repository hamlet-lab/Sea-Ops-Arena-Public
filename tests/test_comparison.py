from pathlib import Path

from sea_ops_arena.comparison import compare_decision_files, comparison_to_markdown


SUITE = Path("examples/scenarios/public_suite_v2.json")
DECISIONS = [
    Path("examples/decisions/v2-balanced.json"),
    Path("examples/decisions/v2-eager.json"),
    Path("examples/decisions/v2-cautious.json"),
]


def test_compare_v2_profiles_side_by_side():
    rows = compare_decision_files(SUITE, DECISIONS)

    assert len(rows) == 3
    assert rows[0].run.summary.decision_matches == 12
    assert rows[1].run.summary.unnecessary_executions == 7
    assert rows[2].run.summary.missed_executions == 5


def test_comparison_markdown_keeps_raw_metrics_without_ranking():
    rows = compare_decision_files(SUITE, DECISIONS)
    report = comparison_to_markdown(rows)

    assert "v2-balanced.json" in report
    assert "v2-eager.json" in report
    assert "v2-cautious.json" in report
    assert "불필요 실행" in report
    assert "필요한 실행 누락" in report
    assert "순위" in report
    assert "1등" not in report
