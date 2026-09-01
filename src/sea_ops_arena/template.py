from __future__ import annotations

import json
from pathlib import Path

from .artifacts import sha256_file
from .input_packs import load_input_pack
from .io import load_suite
from .public_results import PUBLIC_RESULT_SCHEMA_VERSION


_ALLOWED_KINDS = {"fixture", "model", "human", "external-system"}


def build_public_result_template(
    suite_path: str | Path,
    *,
    label: str,
    kind: str,
    input_pack_path: str | Path | None = None,
    model_name: str | None = None,
    model_version: str | None = None,
    recorded_at: str | None = None,
    repeat_id: str | None = None,
) -> dict[str, object]:
    """원본 로그 복사 없이 채울 수 있는 최소 공개 결과 템플릿을 만든다."""

    if not label.strip():
        raise ValueError("label은 비어 있을 수 없습니다")
    if kind not in _ALLOWED_KINDS:
        raise ValueError("지원하지 않는 source.kind입니다")
    if kind == "model" and not model_name:
        raise ValueError("model 결과 템플릿에는 model_name이 필요합니다")

    suite_path = Path(suite_path)
    suite = load_suite(suite_path)
    suite_hash = sha256_file(suite_path)

    input_pack_hash: str | None = None
    if kind != "fixture":
        if input_pack_path is None:
            raise ValueError(
                "fixture가 아닌 결과 템플릿에는 정답 비노출 input_pack_path가 필요합니다"
            )
        input_pack_path = Path(input_pack_path)
        input_pack = load_input_pack(input_pack_path)
        if input_pack["source_suite"]["sha256"] != suite_hash:
            raise ValueError(
                "입력팩의 source_suite.sha256이 현재 시나리오 파일과 일치하지 않습니다"
            )
        input_pack_hash = sha256_file(input_pack_path)
    elif input_pack_path is not None:
        input_pack_path = Path(input_pack_path)
        input_pack = load_input_pack(input_pack_path)
        if input_pack["source_suite"]["sha256"] != suite_hash:
            raise ValueError(
                "입력팩의 source_suite.sha256이 현재 시나리오 파일과 일치하지 않습니다"
            )
        input_pack_hash = sha256_file(input_pack_path)

    source: dict[str, str] = {"kind": kind}
    optional_source = {
        "model_name": model_name,
        "model_version": model_version,
        "recorded_at": recorded_at,
        "repeat_id": repeat_id,
    }
    for key, value in optional_source.items():
        if value is not None:
            if not value.strip():
                raise ValueError(f"{key}은 비어 있는 문자열일 수 없습니다")
            source[key] = value

    template: dict[str, object] = {
        "schema_version": PUBLIC_RESULT_SCHEMA_VERSION,
        "label": label,
        "suite_sha256": suite_hash,
        "source": source,
        "decisions": {
            case.request.request_id: "__FILL__" for case in suite.cases
        },
    }
    if input_pack_hash is not None:
        template["input_pack_sha256"] = input_pack_hash
    return template


def write_public_result_template(
    suite_path: str | Path,
    output_path: str | Path,
    *,
    label: str,
    kind: str,
    input_pack_path: str | Path | None = None,
    model_name: str | None = None,
    model_version: str | None = None,
    recorded_at: str | None = None,
    repeat_id: str | None = None,
) -> Path:
    """검토 후 최종 판단값만 채우도록 공개 결과 템플릿을 JSON으로 저장한다."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    template = build_public_result_template(
        suite_path,
        label=label,
        kind=kind,
        input_pack_path=input_pack_path,
        model_name=model_name,
        model_version=model_version,
        recorded_at=recorded_at,
        repeat_id=repeat_id,
    )
    output_path.write_text(
        json.dumps(template, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path
