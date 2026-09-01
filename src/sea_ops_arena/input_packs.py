from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .artifacts import sha256_file


INPUT_PACK_SCHEMA_VERSION = "arena-input-pack-v1"
_ALLOWED_TOP_LEVEL = {"schema_version", "source_suite", "title", "description", "cases"}
_ALLOWED_SOURCE_SUITE = {"suite_id", "sha256"}
_ALLOWED_CASE_FIELDS = {"case_id", "title", "description", "request"}
_ALLOWED_REQUEST_FIELDS = {"request_id", "scenario_id", "action", "target", "parameters"}
_FORBIDDEN_EVALUATION_FIELDS = {
    "expected_decision",
    "environment_status",
    "tags",
    "notes",
    "metadata",
}


def _require_dict(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{location}은 JSON 객체여야 합니다")
    return value


def _require_allowed_keys(data: dict[str, Any], allowed: set[str], location: str) -> None:
    unexpected = sorted(set(data) - allowed)
    if unexpected:
        raise ValueError(
            f"{location}에 입력팩에서 허용하지 않은 필드가 있습니다: "
            + ", ".join(unexpected)
        )


def build_input_pack(suite_path: str | Path) -> dict[str, object]:
    """평가 정답과 부가 메타데이터를 제외한 모델용 공개 입력팩을 만든다.

    이 함수는 기존 JSON을 복사한 뒤 일부 키를 지우는 방식이 아니라,
    허용된 공개 입력 필드만 새 객체에 다시 작성한다.
    """

    path = Path(suite_path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    data = _require_dict(raw, "시나리오 파일 최상위")

    raw_cases = data.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("cases는 하나 이상의 사례를 포함한 배열이어야 합니다")

    cases: list[dict[str, object]] = []
    for index, item in enumerate(raw_cases, start=1):
        case = _require_dict(item, f"cases[{index}]")
        request = _require_dict(case.get("request"), f"cases[{index}].request")

        if request.get("context_refs"):
            raise ValueError(
                f"cases[{index}].request.context_refs는 입력팩 v1에서 허용하지 않습니다"
            )
        if request.get("metadata"):
            raise ValueError(
                f"cases[{index}].request.metadata는 입력팩 v1에서 허용하지 않습니다"
            )

        public_request: dict[str, object] = {
            "request_id": str(request["request_id"]),
            "scenario_id": str(request["scenario_id"]),
            "action": str(request["action"]),
            "parameters": dict(request.get("parameters", {})),
        }
        if request.get("target") is not None:
            public_request["target"] = str(request["target"])

        cases.append(
            {
                "case_id": str(case["case_id"]),
                "title": str(case["title"]),
                "description": str(case.get("description", "")),
                "request": public_request,
            }
        )

    return {
        "schema_version": INPUT_PACK_SCHEMA_VERSION,
        "source_suite": {
            "suite_id": str(data["suite_id"]),
            "sha256": sha256_file(path),
        },
        "title": str(data["title"]),
        "description": str(data.get("description", "")),
        "cases": cases,
    }


def write_input_pack(suite_path: str | Path, output_path: str | Path) -> Path:
    """모델 입력용 공개 입력팩을 JSON 파일로 저장한다."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(build_input_pack(suite_path), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output


def load_input_pack(path: str | Path) -> dict[str, Any]:
    """입력팩이 허용 필드만 포함하는지 엄격하게 검증해 읽는다."""

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    data = _require_dict(raw, "입력팩 최상위")
    _require_allowed_keys(data, _ALLOWED_TOP_LEVEL, "입력팩 최상위")

    if data.get("schema_version") != INPUT_PACK_SCHEMA_VERSION:
        raise ValueError("지원하지 않는 입력팩 schema_version입니다")

    source_suite = _require_dict(data.get("source_suite"), "source_suite")
    _require_allowed_keys(source_suite, _ALLOWED_SOURCE_SUITE, "source_suite")

    raw_cases = data.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("입력팩 cases는 하나 이상의 사례를 포함해야 합니다")

    for index, item in enumerate(raw_cases, start=1):
        case = _require_dict(item, f"cases[{index}]")
        forbidden = sorted(set(case) & _FORBIDDEN_EVALUATION_FIELDS)
        if forbidden:
            raise ValueError(
                f"cases[{index}]에 평가 전용 필드가 포함되어 있습니다: "
                + ", ".join(forbidden)
            )
        _require_allowed_keys(case, _ALLOWED_CASE_FIELDS, f"cases[{index}]")

        request = _require_dict(case.get("request"), f"cases[{index}].request")
        _require_allowed_keys(request, _ALLOWED_REQUEST_FIELDS, f"cases[{index}].request")

    return data
