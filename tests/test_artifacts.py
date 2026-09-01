from __future__ import annotations

import json
from pathlib import Path

from sea_ops_arena.artifacts import build_manifest, write_run_bundle
from sea_ops_arena.benchmark import run_suite
from sea_ops_arena.fixtures import ScriptedController, SyntheticEnvironment
from sea_ops_arena.io import load_decisions, load_suite


SUITE = Path("examples/scenarios/public_demo_v1.json")
DECISIONS = Path("examples/decisions/balanced.json")


def _run():
    suite = load_suite(SUITE)
    decisions = load_decisions(DECISIONS)
    environment = SyntheticEnvironment(
        outcomes={case.request.request_id: case.environment_status for case in suite.cases}
    )
    return run_suite(suite, ScriptedController(decisions), environment)


def test_manifest_is_deterministic_for_same_public_inputs():
    run = _run()
    first = build_manifest(run, SUITE, DECISIONS)
    second = build_manifest(run, SUITE, DECISIONS)

    assert first == second
    assert len(first["run_id"]) == 20
    assert first["suite"]["case_count"] == 3
    assert len(first["suite"]["sha256"]) == 64
    assert len(first["decisions"]["sha256"]) == 64


def test_run_bundle_writes_public_artifacts(tmp_path):
    run = _run()
    run_dir = write_run_bundle(run, SUITE, DECISIONS, tmp_path)

    assert (run_dir / "report.md").is_file()
    assert (run_dir / "results.json").is_file()
    assert (run_dir / "manifest.json").is_file()

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert run_dir.name == manifest["run_id"]
    assert manifest["summary"]["decision_match_rate"] == 1.0
