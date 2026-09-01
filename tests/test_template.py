from pathlib import Path

import pytest

from sea_ops_arena.artifacts import sha256_file
from sea_ops_arena.template import build_public_result_template


SUITE = Path("examples/scenarios/public_suite_v2.json")


def test_template_contains_only_safe_public_surface():
    template = build_public_result_template(
        SUITE,
        label="example-model-repeat",
        kind="model",
        model_name="public-example-model",
        model_version="2026-09",
        repeat_id="run-001",
    )

    assert set(template) == {
        "schema_version",
        "label",
        "suite_sha256",
        "source",
        "decisions",
    }
    assert template["suite_sha256"] == sha256_file(SUITE)
    assert len(template["decisions"]) == 12
    assert set(template["decisions"].values()) == {"__FILL__"}
    assert set(template["source"]) == {
        "kind",
        "model_name",
        "model_version",
        "repeat_id",
    }


def test_model_template_requires_public_model_name():
    with pytest.raises(ValueError, match="model_name"):
        build_public_result_template(
            SUITE,
            label="missing-model-name",
            kind="model",
        )
