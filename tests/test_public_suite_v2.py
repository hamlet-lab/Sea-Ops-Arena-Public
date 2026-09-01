from pathlib import Path

from sea_ops_arena.benchmark import run_suite
from sea_ops_arena.fixtures import ScriptedController, SyntheticEnvironment
from sea_ops_arena.io import load_decisions, load_suite


SUITE_PATH = Path("examples/scenarios/public_suite_v2.json")


def _run(profile: str):
    suite = load_suite(SUITE_PATH)
    decisions = load_decisions(Path(f"examples/decisions/v2-{profile}.json"))
    environment = SyntheticEnvironment(
        outcomes={case.request.request_id: case.environment_status for case in suite.cases}
    )
    return suite, run_suite(suite, ScriptedController(decisions), environment)


def test_v2_suite_has_public_domain_balance():
    suite = load_suite(SUITE_PATH)

    assert len(suite.cases) == 12
    domains = {case.request.scenario_id for case in suite.cases}
    assert domains == {"customer-support", "office-ops", "inventory", "facility-ops"}
    assert all("synthetic" in case.tags for case in suite.cases)


def test_v2_balanced_profile_matches_public_answer_key():
    _, run = _run("balanced")

    assert run.summary.total_cases == 12
    assert run.summary.decision_matches == 12
    assert run.summary.decision_match_rate == 1.0
    assert run.summary.unnecessary_executions == 0
    assert run.summary.missed_executions == 0
    assert run.summary.attempted_executions == 5
    assert run.summary.successful_executions == 5


def test_v2_eager_profile_surfaces_over_execution():
    _, run = _run("eager")

    assert run.summary.decision_matches == 5
    assert run.summary.unnecessary_executions == 7
    assert run.summary.missed_executions == 0
    assert run.summary.attempted_executions == 12


def test_v2_cautious_profile_surfaces_missed_work():
    _, run = _run("cautious")

    assert run.summary.decision_matches == 3
    assert run.summary.unnecessary_executions == 0
    assert run.summary.missed_executions == 5
    assert run.summary.attempted_executions == 0
