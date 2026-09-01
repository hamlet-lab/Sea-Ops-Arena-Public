from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .contracts import DecisionStatus, ExecutionRequest, ExecutionStatus
from .scenarios import BenchmarkCase, BenchmarkSuite


def _read_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON 최상위 값은 객체여야 합니다")
    return data


def load_suite(path: str | Path) -> BenchmarkSuite:
    """공개 JSON 파일에서 벤치마크 시나리오 묶음을 읽는다."""

    data = _read_json(path)
    raw_cases = data.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("cases는 하나 이상의 사례를 포함한 배열이어야 합니다")

    cases: list[BenchmarkCase] = []
    seen_case_ids: set[str] = set()
    seen_request_ids: set[str] = set()

    for raw_case in raw_cases:
        if not isinstance(raw_case, dict):
            raise ValueError("각 사례는 JSON 객체여야 합니다")
        raw_request = raw_case.get("request")
        if not isinstance(raw_request, dict):
            raise ValueError("각 사례에는 request 객체가 필요합니다")

        case_id = str(raw_case["case_id"])
        request_id = str(raw_request["request_id"])
        if case_id in seen_case_ids:
            raise ValueError(f"중복 case_id: {case_id}")
        if request_id in seen_request_ids:
            raise ValueError(f"중복 request_id: {request_id}")
        seen_case_ids.add(case_id)
        seen_request_ids.add(request_id)

        request = ExecutionRequest(
            request_id=request_id,
            scenario_id=str(raw_request["scenario_id"]),
            action=str(raw_request["action"]),
            target=(
                None
                if raw_request.get("target") is None
                else str(raw_request["target"])
            ),
            parameters=dict(raw_request.get("parameters", {})),
            context_refs=tuple(str(item) for item in raw_request.get("context_refs", [])),
            metadata=dict(raw_request.get("metadata", {})),
        )
        cases.append(
            BenchmarkCase(
                case_id=case_id,
                title=str(raw_case["title"]),
                description=str(raw_case.get("description", "")),
                request=request,
                expected_decision=DecisionStatus(str(raw_case["expected_decision"])),
                environment_status=ExecutionStatus(
                    str(raw_case.get("environment_status", "executed"))
                ),
                tags=tuple(str(item) for item in raw_case.get("tags", [])),
                notes=(None if raw_case.get("notes") is None else str(raw_case["notes"])),
            )
        )

    return BenchmarkSuite(
        suite_id=str(data["suite_id"]),
        title=str(data["title"]),
        description=str(data.get("description", "")),
        cases=tuple(cases),
        metadata={str(key): str(value) for key, value in data.get("metadata", {}).items()},
    )


def load_decisions(path: str | Path) -> dict[str, DecisionStatus]:
    """공개 JSON 파일에서 요청별 판단 결과를 읽는다."""

    data = _read_json(path)
    raw_decisions = data.get("decisions")
    if not isinstance(raw_decisions, dict) or not raw_decisions:
        raise ValueError("decisions는 하나 이상의 요청별 결과를 포함한 객체여야 합니다")

    return {
        str(request_id): DecisionStatus(str(status))
        for request_id, status in raw_decisions.items()
    }
