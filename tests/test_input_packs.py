from __future__ import annotations

import json
from pathlib import Path

import pytest

from sea_ops_arena.input_packs import build_input_pack, load_input_pack, write_input_pack


SUITE = Path("examples/scenarios/public_suite_v2.json")


def test_input_pack_excludes_evaluation_only_fields(tmp_path):
    output = tmp_path / "model-input.json"
    write_input_pack(SUITE, output)
    data = load_input_pack(output)

    assert data["schema_version"] == "arena-input-pack-v1"
    assert len(data["cases"]) == 12

    raw_text = output.read_text(encoding="utf-8")
    assert "expected_decision" not in raw_text
    assert '"tags"' not in raw_text
    assert '"notes"' not in raw_text
    assert '"metadata"' not in raw_text
    assert '"environment_status"' not in raw_text


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
