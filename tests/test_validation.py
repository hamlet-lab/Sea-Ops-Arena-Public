import json
from pathlib import Path

import pytest

from sea_ops_arena.artifacts import sha256_file
from sea_ops_arena.contracts import DecisionStatus
from sea_ops_arena.input_packs import write_input_pack
from sea_ops_arena.io import load_decisions, load_suite
from sea_ops_arena.validation import (
    inspect_decision_coverage,
    validate_decision_coverage,
    validate_public_result_binding,
)


SUITE_PATH = Path("examples/scenarios/public_suite_v2.json")
SUITE = load_suite(SUITE_PATH)


def test_complete_v2_decisions_pass_validation():
    decisions = load_decisions(Path("examples/decisions/v2-balanced.json"))

    coverage = inspect_decision_coverage(SUITE, decisions)
    assert coverage.is_complete
    validate_decision_coverage(SUITE, decisions)


def test_missing_request_id_is_reported():
    decisions = load_decisions(Path("examples/decisions/v2-balanced.json"))
    decisions.pop("v2-cs-01")

    coverage = inspect_decision_coverage(SUITE, decisions)
    assert coverage.missing_request_ids == ("v2-cs-01",)

    with pytest.raises(ValueError, match="v2-cs-01"):
        validate_decision_coverage(SUITE, decisions)


def test_unexpected_request_id_is_reported():
    decisions = load_decisions(Path("examples/decisions/v2-balanced.json"))
    decisions["not-in-suite"] = DecisionStatus.PROCEED

    coverage = inspect_decision_coverage(SUITE, decisions)
    assert coverage.unexpected_request_ids == ("not-in-suite",)

    with pytest.raises(ValueError, match="not-in-suite"):
        validate_decision_coverage(SUITE, decisions)


def _write_model_result(tmp_path: Path, input_pack: Path) -> Path:
    decisions = json.loads(
        Path("examples/decisions/v2-balanced.json").read_text(encoding="utf-8")
    )["decisions"]
    result = {
        "schema_version": "public-decision-set-v1",
        "label": "model-binding-test",
        "suite_sha256": sha256_file(SUITE_PATH),
        "input_pack_sha256": sha256_file(input_pack),
        "source": {
            "kind": "model",
            "model_name": "public-test-model",
            "model_version": "test",
            "repeat_id": "run-001",
        },
        "decisions": decisions,
    }
    path = tmp_path / "model.public.json"
    path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    return path


def test_model_result_requires_input_pack_path(tmp_path):
    input_pack = tmp_path / "model-input.json"
    write_input_pack(SUITE_PATH, input_pack)
    result = _write_model_result(tmp_path, input_pack)

    with pytest.raises(ValueError, match="--input-pack"):
        validate_public_result_binding(SUITE_PATH, result)


def test_model_result_accepts_exact_input_pack(tmp_path):
    input_pack = tmp_path / "model-input.json"
    write_input_pack(SUITE_PATH, input_pack)
    result = _write_model_result(tmp_path, input_pack)

    validate_public_result_binding(SUITE_PATH, result, input_pack)


def test_model_result_rejects_modified_input_pack(tmp_path):
    input_pack = tmp_path / "model-input.json"
    write_input_pack(SUITE_PATH, input_pack)
    result = _write_model_result(tmp_path, input_pack)

    data = json.loads(input_pack.read_text(encoding="utf-8"))
    data["cases"][0]["description"] += " 변경"
    input_pack.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="input_pack_sha256"):
        validate_public_result_binding(SUITE_PATH, result, input_pack)
