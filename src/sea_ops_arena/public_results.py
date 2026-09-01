from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contracts import DecisionStatus


PUBLIC_RESULT_SCHEMA_VERSION = "public-decision-set-v1"
_ALLOWED_TOP_LEVEL = {"schema_version", "label", "source", "decisions"}
_ALLOWED_SOURCE_FIELDS = {
    "kind",
    "model_name",
    "model_version",
    "recorded_at",
    "repeat_id",
}
_ALLOWED_SOURCE_KINDS = {"fixture", "model", "human", "external-system"}


@dataclass(frozen=True)
class PublicResultSource:
    kind: str
    model_name: str | None = None
    model_version: str | None = None
    recorded_at: str | None = None
    repeat_id: str | None = None


@dataclass(frozen=True)
class PublicDecisionSet:
    schema_version: str
    label: str
    source: PublicResultSource
    decisions: dict[str, DecisionStatus]


def _require_allowed_keys(data: dict[str, Any], allowed: set[str], location: str) -> None:
    unexpected = sorted(set(data) - allowed)
    if unexpected:
        raise ValueError(
            f"{location}에 공개 포맷에서 허용하지 않은 필드가 있습니다: "
            + ", ".join(unexpected)
        )


def load_public_decision_set(path: str | Path) -> PublicDecisionSet:
    """허용 필드만 가진 공개 결과 파일을 엄격하게 읽는다.

    공개 결과 포맷은 임의 metadata를 허용하지 않는다. 공개 검토를 거친 최소한의
    출처 정보와 판단 결과만 저장해, 원본 프롬프트·로그·내부 trace 등이 실수로
    함께 배포되는 위험을 줄인다.
    """

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("공개 결과 JSON 최상위 값은 객체여야 합니다")
    _require_allowed_keys(raw, _ALLOWED_TOP_LEVEL, "최상위")

    schema_version = str(raw.get("schema_version", ""))
    if schema_version != PUBLIC_RESULT_SCHEMA_VERSION:
        raise ValueError(
            f"지원하지 않는 공개 결과 schema_version: {schema_version or '(없음)'}"
        )

    label = raw.get("label")
    if not isinstance(label, str) or not label.strip():
        raise ValueError("label은 비어 있지 않은 문자열이어야 합니다")

    raw_source = raw.get("source")
    if not isinstance(raw_source, dict):
        raise ValueError("source 객체가 필요합니다")
    _require_allowed_keys(raw_source, _ALLOWED_SOURCE_FIELDS, "source")

    kind = raw_source.get("kind")
    if kind not in _ALLOWED_SOURCE_KINDS:
        raise ValueError(
            "source.kind는 fixture, model, human, external-system 중 하나여야 합니다"
        )

    def optional_text(name: str) -> str | None:
        value = raw_source.get(name)
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"source.{name}은 비어 있지 않은 문자열이어야 합니다")
        return value

    raw_decisions = raw.get("decisions")
    if not isinstance(raw_decisions, dict) or not raw_decisions:
        raise ValueError("decisions는 하나 이상의 요청별 결과를 포함한 객체여야 합니다")

    decisions: dict[str, DecisionStatus] = {}
    for request_id, status in raw_decisions.items():
        request_key = str(request_id)
        if not request_key:
            raise ValueError("빈 request_id는 사용할 수 없습니다")
        decisions[request_key] = DecisionStatus(str(status))

    return PublicDecisionSet(
        schema_version=schema_version,
        label=label,
        source=PublicResultSource(
            kind=str(kind),
            model_name=optional_text("model_name"),
            model_version=optional_text("model_version"),
            recorded_at=optional_text("recorded_at"),
            repeat_id=optional_text("repeat_id"),
        ),
        decisions=decisions,
    )
