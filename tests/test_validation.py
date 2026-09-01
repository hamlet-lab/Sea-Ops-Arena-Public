from pathlib import Path

import pytest

from sea_ops_arena.contracts import DecisionStatus
from sea_ops_arena.io import load_decisions, load_suite
from sea_ops_arena.validation import inspect_decision_coverage, validate_decision_coverage


SUITE = load_suite(Path("examples/scenarios/public_suite_v2.json"))


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
