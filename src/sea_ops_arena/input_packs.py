from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .artifacts import sha256_file


INPUT_PACK_SCHEMA_VERSION = "arena-input-pack-v2"
TASK_ID = "public-decision-classification-v1"
_ALLOWED_TOP_LEVEL = {
    "schema_version",
    "source_suite",
    "task",
    "title",
    "description",
    "cases",
}
_ALLOWED_SOURCE_SUITE = {"suite_id", "sha256"}
_ALLOWED_TASK_FIELDS = {"task_id", "instruction", "status_meanings", "output_contract"}
_ALLOWED_STATUS_MEANINGS = {"proceed", "reject", "defer"}
_ALLOWED_OUTPUT_CONTRACT = {"format", "required_request_ids", "allowed_values"}
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


def _task_spec(request_ids: list[str]) -> dict[str, object]:
    """특정 비공개 구현과 무관한 공개 벤치마크 과제 정의."""

    return {
        "task_id": TASK_ID,
        "instruction": (
            "각 사례에 제공된 공개 정보만 사용하여 요청된 행동을 진행할지, "
            "거부할지, 추가 확인을 위해 보류할지 판단하세요. 내부 추론 과정이나 "
            "설명은 제출하지 말고 request_id별 최종 상태만 제출하세요."
        ),
        "status_meanings": {
            "proceed": "제공된 정보가 충분하고 서로 모순되지 않아 요청된 행동을 진행할 수 있음",
            "reject": "제공된 정보만으로 요청된 행동을 그대로 수행하면 안 된다는 사실이 명확함",
            "defer": "판단 전에 추가 정보가 필요하거나 제공된 정보 사이의 충돌을 먼저 해소해야 함",
        },
        "output_contract": {
            "format": "request_id_to_status_map",
            "required_request_ids": request_ids,
            "allowed_values": ["proceed", "reject", "defer"],
        },
    }


def build_input_pack(suite_path: str | Path) -> dict[str, object]:
    """평가 정답을 제외하고 공개 과제까지 고정한 모델 입력팩을 만든다.

    원본 JSON에서 키를 삭제하는 방식이 아니라, 허용된 공개 입력 필드만 새 객체에
    다시 작성한다. 입력팩의 SHA-256은 사례와 과제 정의 전체를 함께 고정한다.
    """

    path = Path(suite_path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    data = _require_dict(raw, "시나리오 파일 최상위")

    raw_cases = data.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("cases는 하나 이상의 사례를 포함한 배열이어야 합니다")

    cases: list[dict[str, object]] = []
    request_ids: list[str] = []
    for index, item in enumerate(raw_cases, start=1):
        case = _require_dict(item, f"cases[{index}]")
        request = _require_dict(case.get("request"), f"cases[{index}].request")

        if request.get("context_refs"):
            raise ValueError(
                f"cases[{index}].request.context_refs는 입력팩 v2에서 허용하지 않습니다"
            )
        if request.get("metadata"):
            raise ValueError(
                f"cases[{index}].request.metadata는 입력팩 v2에서 허용하지 않습니다"
            )

        request_id = str(request["request_id"])
        request_ids.append(request_id)
        public_request: dict[str, object] = {
            "request_id": request_id,
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
        "task": _task_spec(request_ids),
        "title": str(data["title"]),
        "description": str(data.get("description", "")),
        "cases": cases,
    }


def write_input_pack(suite_path: str | Path, output_path: str | Path) -> Path:
    """모델이 그대로 받을 수 있는 공개 입력팩을 JSON 파일로 저장한다."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(build_input_pack(suite_path), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output


def load_input_pack(path: str | Path) -> dict[str, Any]:
    """입력팩이 허용 필드와 공개 과제 계약만 포함하는지 엄격하게 검증한다."""

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    data = _require_dict(raw, "입력팩 최상위")
    _require_allowed_keys(data, _ALLOWED_TOP_LEVEL, "입력팩 최상위")

    if data.get("schema_version") != INPUT_PACK_SCHEMA_VERSION:
        raise ValueError("지원하지 않는 입력팩 schema_version입니다")

    source_suite = _require_dict(data.get("source_suite"), "source_suite")
    _require_allowed_keys(source_suite, _ALLOWED_SOURCE_SUITE, "source_suite")

    task = _require_dict(data.get("task"), "task")
    _require_allowed_keys(task, _ALLOWED_TASK_FIELDS, "task")
    if task.get("task_id") != TASK_ID:
        raise ValueError("지원하지 않는 task.task_id입니다")

    status_meanings = _require_dict(task.get("status_meanings"), "task.status_meanings")
    _require_allowed_keys(status_meanings, _ALLOWED_STATUS_MEANINGS, "task.status_meanings")
    if set(status_meanings) != _ALLOWED_STATUS_MEANINGS:
        raise ValueError("task.status_meanings에는 proceed, reject, defer가 모두 필요합니다")

    output_contract = _require_dict(task.get("output_contract"), "task.output_contract")
    _require_allowed_keys(output_contract, _ALLOWED_OUTPUT_CONTRACT, "task.output_contract")
    if output_contract.get("format") != "request_id_to_status_map":
        raise ValueError("지원하지 않는 task.output_contract.format입니다")
    if output_contract.get("allowed_values") != ["proceed", "reject", "defer"]:
        raise ValueError("task.output_contract.allowed_values가 표준 값과 일치하지 않습니다")

    raw_cases = data.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("입력팩 cases는 하나 이상의 사례를 포함해야 합니다")

    case_request_ids: list[str] = []
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
        case_request_ids.append(str(request.get("request_id", "")))

    if output_contract.get("required_request_ids") != case_request_ids:
        raise ValueError(
            "task.output_contract.required_request_ids가 cases의 request_id 순서와 일치하지 않습니다"
        )

    return data
