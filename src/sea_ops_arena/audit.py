from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .artifacts import sha256_file
from .input_packs import INPUT_PACK_SCHEMA_VERSION, load_input_pack
from .public_results import load_public_decision_set


_BLOCKED_DIR_NAMES = {"private", "internal", "traces"}
_BLOCKED_FILE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}


@dataclass(frozen=True)
class AuditFinding:
    code: str
    path: str
    message: str


def _iter_public_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in {".git", ".venv", "venv", "__pycache__"} for part in relative.parts):
            continue
        yield path, relative


def audit_repository(root: str | Path = ".") -> tuple[AuditFinding, ...]:
    """비밀명 목록 없이 일반적인 공개 저장소 위험 신호를 검사한다.

    이 감사는 전용 보안 검토를 대체하지 않는다. 공개 저장소 안에 내부 명칭
    deny-list를 두지 않으면서도, 흔한 민감 파일과 공개 결과 포맷 오류를 조기에
    발견하는 보조 방어선이다.
    """

    root = Path(root).resolve()
    findings: list[AuditFinding] = []
    public_files = list(_iter_public_files(root))

    scenario_hashes: set[str] = set()
    scenario_dir = root / "examples" / "scenarios"
    if scenario_dir.exists():
        for scenario in scenario_dir.glob("*.json"):
            scenario_hashes.add(sha256_file(scenario))

    input_pack_hashes: set[str] = set()
    for path, relative in public_files:
        if path.suffix.lower() != ".json":
            continue
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(raw, dict) or raw.get("schema_version") != INPUT_PACK_SCHEMA_VERSION:
            continue
        try:
            load_input_pack(path)
        except (OSError, ValueError) as exc:
            findings.append(
                AuditFinding(
                    code="invalid-input-pack",
                    path=str(relative),
                    message=str(exc),
                )
            )
        else:
            input_pack_hashes.add(sha256_file(path))

    for path, relative in public_files:
        lowered_parts = {part.lower() for part in relative.parts[:-1]}
        blocked_dirs = sorted(lowered_parts & _BLOCKED_DIR_NAMES)
        if blocked_dirs:
            findings.append(
                AuditFinding(
                    code="blocked-directory",
                    path=str(relative),
                    message="공개 저장소에서 사용하지 않는 디렉터리 경로가 포함되어 있습니다: "
                    + ", ".join(blocked_dirs),
                )
            )

        name_lower = relative.name.lower()
        if name_lower == ".env" or name_lower.startswith(".env."):
            findings.append(
                AuditFinding(
                    code="environment-file",
                    path=str(relative),
                    message="환경 변수 파일은 공개 저장소에 포함하지 않습니다",
                )
            )

        if path.suffix.lower() in _BLOCKED_FILE_SUFFIXES:
            findings.append(
                AuditFinding(
                    code="credential-file",
                    path=str(relative),
                    message="키 또는 인증서 형식 파일은 공개 저장소에 포함하지 않습니다",
                )
            )

        if relative.name.endswith(".public.json"):
            try:
                result_set = load_public_decision_set(path)
            except (OSError, ValueError) as exc:
                findings.append(
                    AuditFinding(
                        code="invalid-public-result",
                        path=str(relative),
                        message=str(exc),
                    )
                )
                continue

            if result_set.source.kind != "fixture":
                if result_set.suite_sha256 is None:
                    findings.append(
                        AuditFinding(
                            code="missing-suite-hash",
                            path=str(relative),
                            message="실제 외부 공개 결과에는 suite_sha256이 필요합니다",
                        )
                    )
                elif scenario_hashes and result_set.suite_sha256 not in scenario_hashes:
                    findings.append(
                        AuditFinding(
                            code="unknown-suite-hash",
                            path=str(relative),
                            message="suite_sha256과 일치하는 공개 예제 시나리오 파일을 찾지 못했습니다",
                        )
                    )

                if result_set.input_pack_sha256 is None:
                    findings.append(
                        AuditFinding(
                            code="missing-input-pack-hash",
                            path=str(relative),
                            message="실제 외부 공개 결과에는 input_pack_sha256이 필요합니다",
                        )
                    )
                elif result_set.input_pack_sha256 not in input_pack_hashes:
                    findings.append(
                        AuditFinding(
                            code="unknown-input-pack-hash",
                            path=str(relative),
                            message="input_pack_sha256과 일치하는 정답 비노출 입력팩 파일을 저장소에서 찾지 못했습니다",
                        )
                    )

    return tuple(findings)
