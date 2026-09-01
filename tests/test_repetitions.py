from pathlib import Path

import pytest

from sea_ops_arena.repetitions import evaluate_repeated_results


SUITE = Path("examples/scenarios/public_suite_v2.json")
RESULTS = [
    Path("examples/results/v2-balanced.public.json"),
    Path("examples/results/v2-repeat-002.public.json"),
    Path("examples/results/v2-repeat-003.public.json"),
]


def test_repeat_evaluation_measures_public_output_stability():
    evaluation = evaluate_repeated_results(SUITE, RESULTS)

    assert evaluation.summary.repeat_count == 3
    assert evaluation.summary.total_cases == 12
    assert evaluation.summary.stable_cases == 11
    assert evaluation.summary.stability_rate == pytest.approx(11 / 12)
    assert evaluation.summary.decision_match_rate_mean == pytest.approx(35 / 36)
    assert evaluation.summary.decision_match_rate_min == pytest.approx(11 / 12)
    assert evaluation.summary.decision_match_rate_max == 1.0


def test_repeat_evaluation_rejects_duplicate_repeat_id(tmp_path):
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text(RESULTS[0].read_text(encoding="utf-8"), encoding="utf-8")

    with pytest.raises(ValueError, match="중복 repeat_id"):
        evaluate_repeated_results(SUITE, [RESULTS[0], duplicate])


def test_repeat_evaluation_requires_same_public_identity(tmp_path):
    changed = RESULTS[1].read_text(encoding="utf-8").replace(
        '"model_version": "v1"', '"model_version": "v2"'
    )
    path = tmp_path / "changed.json"
    path.write_text(changed, encoding="utf-8")

    with pytest.raises(ValueError, match="서로 일치하지 않습니다"):
        evaluate_repeated_results(SUITE, [RESULTS[0], path])
