from pathlib import Path

from sea_ops_arena.benchmark import run_suite
from sea_ops_arena.fixtures import ScriptedController, SyntheticEnvironment
from sea_ops_arena.io import load_decisions, load_suite


EXAMPLES = Path("examples")


def test_public_json_example_loads_and_runs() -> None:
    suite = load_suite(EXAMPLES / "scenarios" / "public_demo_v1.json")
    decisions = load_decisions(EXAMPLES / "decisions" / "balanced.json")
    environment = SyntheticEnvironment(
        outcomes={case.request.request_id: case.environment_status for case in suite.cases}
    )

    run = run_suite(suite, ScriptedController(decisions), environment)

    assert suite.suite_id == "public-demo-v1"
    assert len(suite.cases) == 3
    assert run.summary.decision_matches == 3
    assert run.summary.decision_match_rate == 1.0
