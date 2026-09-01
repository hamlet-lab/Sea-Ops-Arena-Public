from __future__ import annotations

import json
from pathlib import Path

import pytest

from sea_ops_arena.artifacts import sha256_file
from sea_ops_arena.input_packs import write_input_pack
from sea_ops_arena.io import load_decisions, load_suite
from sea_ops_arena.public_results import load_public_decision_set
from sea_ops_arena.validation import (
    validate_decision_coverage,
    validate_public_result_binding,
)


PUBLIC_RESULT = Path("examples/results/v2-balanced.public.json")
SUITE = Path("examples/scenarios/public_suite_v2.json")


def test_strict_public_result_format_loads_and_matches_suite():
    result_set = load_public_decision_set(PUBLIC_RESULT)
    suite = load_suite(SUITE)

    assert result_set.schema_version == "public-decision-set-v1"
    assert result_set.source.kind == "fixture"
    assert result_set.source.model_name == "synthetic-example"
    assert len(result_set.decisions) == 12
    validate_decision_coverage(suite, result_set.decisions)


def test_regular_loader_uses_strict_format_when_schema_version_is_present():
    decisions = load_decisions(PUBLIC_RESULT)
    assert len(decisions) == 12


def test_unknown_top_level_field_is_rejected(tmp_path):
    data = json.loads(PUBLIC_RESULT.read_text(encoding="utf-8"))
    data["prompt"] = "이 필드는 공개 결과 포맷에 허용되지 않음"
    path = tmp_path / "unsafe.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="허용하지 않은 필드"):
        load_public_decision_set(path)


def test_unknown_source_field_is_rejected(tmp_path):
    data = json.loads(PUBLIC_RESULT.read_text(encoding="utf-8"))
    data["source"]["trace"] = "임의 내부 로그"
    path = tmp_path / "unsafe-source.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="허용하지 않은 필드"):
        load_public_decision_set(path)


def test_non_fixture_result_requires_suite_hash(tmp_path):
    data = json.loads(PUBLIC_RESULT.read_text(encoding="utf-8"))
    data["source"]["kind"] = "model"
    data["source"]["model_name"] = "public-example-model"
    data.pop("suite_sha256", None)
    path = tmp_path / "model-result.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="suite_sha256"):
        validate_public_result_binding(SUITE, path)


def test_non_fixture_result_requires_input_pack_hash(tmp_path):
    data = json.loads(PUBLIC_RESULT.read_text(encoding="utf-8"))
    data["source"]["kind"] = "model"
    data["source"]["model_name"] = "public-example-model"
    data["suite_sha256"] = sha256_file(SUITE)
    data.pop("input_pack_sha256", None)
    path = tmp_path / "model-result.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="input_pack_sha256"):
        validate_public_result_binding(SUITE, path)


def test_suite_and_input_pack_binding_accept_exact_files_and_reject_mismatch(tmp_path):
    input_pack = tmp_path / "model-input.json"
    write_input_pack(SUITE, input_pack)

    data = json.loads(PUBLIC_RESULT.read_text(encoding="utf-8"))
    data["source"]["kind"] = "model"
    data["source"]["model_name"] = "public-example-model"
    data["suite_sha256"] = sha256_file(SUITE)
    data["input_pack_sha256"] = sha256_file(input_pack)
    path = tmp_path / "model-result.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    validate_public_result_binding(SUITE, path, input_pack)

    data["suite_sha256"] = "0" * 64
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="suite_sha256"):
        validate_public_result_binding(SUITE, path, input_pack)

    data["suite_sha256"] = sha256_file(SUITE)
    data["input_pack_sha256"] = "0" * 64
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="input_pack_sha256"):
        validate_public_result_binding(SUITE, path, input_pack)
