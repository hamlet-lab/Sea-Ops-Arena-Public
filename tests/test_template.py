from pathlib import Path

import pytest

from sea_ops_arena.artifacts import sha256_file
from sea_ops_arena.input_packs import write_input_pack
from sea_ops_arena.template import build_public_result_template


SUITE = Path("examples/scenarios/public_suite_v2.json")


def test_template_contains_only_safe_public_surface(tmp_path):
    input_pack = tmp_path / "model-input.json"
    write_input_pack(SUITE, input_pack)

    template = build_public_result_template(
        SUITE,
        label="example-model-repeat",
        kind="model",
        input_pack_path=input_pack,
        model_name="public-example-model",
        model_version="2026-09",
        repeat_id="run-001",
    )

    assert set(template) == {
        "schema_version",
        "label",
        "suite_sha256",
        "input_pack_sha256",
        "source",
        "decisions",
    }
    assert template["suite_sha256"] == sha256_file(SUITE)
    assert template["input_pack_sha256"] == sha256_file(input_pack)
    assert len(template["decisions"]) == 12
    assert set(template["decisions"].values()) == {"__FILL__"}
    assert set(template["source"]) == {
        "kind",
        "model_name",
        "model_version",
        "repeat_id",
    }


def test_model_template_requires_public_model_name(tmp_path):
    input_pack = tmp_path / "model-input.json"
    write_input_pack(SUITE, input_pack)

    with pytest.raises(ValueError, match="model_name"):
        build_public_result_template(
            SUITE,
            label="missing-model-name",
            kind="model",
            input_pack_path=input_pack,
        )


def test_non_fixture_template_requires_input_pack():
    with pytest.raises(ValueError, match="input_pack_path"):
        build_public_result_template(
            SUITE,
            label="missing-input-pack",
            kind="model",
            model_name="public-example-model",
        )
