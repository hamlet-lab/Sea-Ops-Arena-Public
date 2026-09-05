from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from sea_ops_arena.input_packs import build_input_pack, load_input_pack, write_input_pack


SUITE = Path("examples/scenarios/public_suite_v2.json")
FROZEN_INPUT_PACK = Path("examples/input_packs/public_suite_v2.input.json")
FROZEN_HASH_FILE = Path("examples/input_packs/public_suite_v2.input.sha256")


def test_input_pack_excludes_evaluation_only_fields(tmp_path):
    output = tmp_path / "model-input.json"
    write_input_pack(SUITE, output)
    data = load_input_pack(output)

    assert data["schema_version"] == "arena-input-pack-v2"
    assert len(data["cases"]) == 12

    raw_text = output.read_text(encoding="utf-8")
    assert "expected_decision" not in raw_text
    assert '"tags"' not in raw_text
    assert '"notes"' not in raw_text
    assert '"metadata"' not in raw_text
    assert '"environment_status"' not in raw_text


def test_input_pack_contains_fixed_public_task_contract():
    data = build_input_pack(SUITE)
    task = data["task"]

    assert task["task_id"] == "public-decision-classification-v1"
    assert set(task["status_meanings"]) == {"proceed", "reject", "defer"}
    assert task["execution_constraints"] == [
        "use_only_input_pack_content",
        "no_external_tools_or_retrieval",
        "return_final_status_map_only",
    ]
    assert task["output_contract"]["allowed_values"] == [
        "proceed",
        "reject",
        "defer",
    ]
    assert task["output_contract"]["required_request_ids"] == [
        case["request"]["request_id"] for case in data["cases"]
    ]


def test_frozen_input_pack_matches_generator_byte_for_byte(tmp_path):
    regenerated = tmp_path / "regenerated.input.json"
    write_input_pack(SUITE, regenerated)

    assert regenerated.read_bytes() == FROZEN_INPUT_PACK.read_bytes()


def test_frozen_input_pack_hash_file_matches_bytes():
    expected_hash, expected_name = FROZEN_HASH_FILE.read_text(encoding="utf-8").strip().split()
    actual_hash = hashlib.sha256(FROZEN_INPUT_PACK.read_bytes()).hexdigest()

    assert expected_name == FROZEN_INPUT_PACK.name
    assert actual_hash == expected_hash
    assert actual_hash == "e68cf82311d4c4b6477799cf61aeb28b4f446d997e5a3c82b3c6ebb9680b88db"


def test_input_pack_keeps_public_request_data():
    data = build_input_pack(SUITE)
    first = data["cases"][0]

    assert first["case_id"] == "cs-refund-ready"
    assert first["request"]["request_id"] == "v2-cs-01"
    assert first["request"]["action"] == "issue_refund"
    assert first["request"]["parameters"]["amount"] == 28000


def test_loader_rejects_injected_expected_decision(tmp_path):
    output = tmp_path / "unsafe-input.json"
    write_input_pack(SUITE, output)
    data = json.loads(output.read_text(encoding="utf-8"))
    data["cases"][0]["expected_decision"] = "proceed"
    output.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="평가 전용 필드"):
        load_input_pack(output)


def test_loader_rejects_modified_execution_constraints(tmp_path):
    output = tmp_path / "unsafe-constraints.json"
    write_input_pack(SUITE, output)
    data = json.loads(output.read_text(encoding="utf-8"))
    data["task"]["execution_constraints"] = ["external_search_allowed"]
    output.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="execution_constraints"):
        load_input_pack(output)


def test_loader_rejects_modified_allowed_values(tmp_path):
    output = tmp_path / "unsafe-task.json"
    write_input_pack(SUITE, output)
    data = json.loads(output.read_text(encoding="utf-8"))
    data["task"]["output_contract"]["allowed_values"] = ["yes", "no"]
    output.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="allowed_values"):
        load_input_pack(output)


def test_loader_rejects_request_id_contract_mismatch(tmp_path):
    output = tmp_path / "unsafe-ids.json"
    write_input_pack(SUITE, output)
    data = json.loads(output.read_text(encoding="utf-8"))
    data["task"]["output_contract"]["required_request_ids"][0] = "different-id"
    output.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="required_request_ids"):
        load_input_pack(output)


def test_generator_rejects_nonempty_request_metadata(tmp_path):
    source = json.loads(SUITE.read_text(encoding="utf-8"))
    source["cases"][0]["request"]["metadata"] = {"unexpected": "value"}
    path = tmp_path / "suite-with-metadata.json"
    path.write_text(json.dumps(source, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="metadata"):
        build_input_pack(path)


def test_generator_rejects_nonempty_context_refs(tmp_path):
    source = json.loads(SUITE.read_text(encoding="utf-8"))
    source["cases"][0]["request"]["context_refs"] = ["some-resource"]
    path = tmp_path / "suite-with-context.json"
    path.write_text(json.dumps(source, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="context_refs"):
        build_input_pack(path)
