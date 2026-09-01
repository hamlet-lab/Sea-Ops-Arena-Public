from sea_ops_arena.demo import run_demo


def test_balanced_profile_matches_all_public_cases() -> None:
    run = run_demo("balanced")

    assert run.summary.total_cases == 3
    assert run.summary.decision_matches == 3
    assert run.summary.decision_match_rate == 1.0
    assert run.summary.unnecessary_executions == 0
    assert run.summary.missed_executions == 0
    assert run.summary.attempted_executions == 1
    assert run.summary.successful_executions == 1


def test_eager_profile_exposes_unnecessary_execution_count() -> None:
    run = run_demo("eager")

    assert run.summary.decision_matches == 1
    assert run.summary.unnecessary_executions == 2
    assert run.summary.missed_executions == 0
    assert run.summary.attempted_executions == 3


def test_cautious_profile_exposes_missed_execution_count() -> None:
    run = run_demo("cautious")

    assert run.summary.decision_matches == 1
    assert run.summary.unnecessary_executions == 0
    assert run.summary.missed_executions == 1
    assert run.summary.attempted_executions == 0
