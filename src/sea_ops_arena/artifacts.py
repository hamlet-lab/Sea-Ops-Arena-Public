from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .benchmark import BenchmarkRun
from .reporting import to_json, to_markdown


BUNDLE_FORMAT_VERSION = "arena-run-v1"


def sha256_file(path: str | Path) -> str:
    """공개 입력 파일의 SHA-256 해시를 계산한다."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(
    run: BenchmarkRun,
    suite_path: str | Path,
    decisions_path: str | Path,
) -> dict[str, object]:
    """내부 구현 정보 없이 공개 입력과 결과의 재현 식별자를 만든다."""

    suite_path = Path(suite_path)
    decisions_path = Path(decisions_path)
    suite_hash = sha256_file(suite_path)
    decisions_hash = sha256_file(decisions_path)
    run_seed = f"{BUNDLE_FORMAT_VERSION}:{suite_hash}:{decisions_hash}".encode("utf-8")
    run_id = hashlib.sha256(run_seed).hexdigest()[:20]

    return {
        "format_version": BUNDLE_FORMAT_VERSION,
        "run_id": run_id,
        "suite": {
            "file": suite_path.name,
            "sha256": suite_hash,
            "suite_id": run.suite_id,
            "case_count": run.summary.total_cases,
        },
        "decisions": {
            "file": decisions_path.name,
            "sha256": decisions_hash,
        },
        "summary": {
            "decision_matches": run.summary.decision_matches,
            "decision_match_rate": run.summary.decision_match_rate,
            "unnecessary_executions": run.summary.unnecessary_executions,
            "missed_executions": run.summary.missed_executions,
            "attempted_executions": run.summary.attempted_executions,
            "successful_executions": run.summary.successful_executions,
        },
    }


def write_run_bundle(
    run: BenchmarkRun,
    suite_path: str | Path,
    decisions_path: str | Path,
    output_dir: str | Path,
) -> Path:
    """Markdown, JSON, manifest를 하나의 공개 실행 결과 디렉터리에 기록한다."""

    manifest = build_manifest(run, suite_path, decisions_path)
    run_dir = Path(output_dir) / str(manifest["run_id"])
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "report.md").write_text(to_markdown(run), encoding="utf-8")
    (run_dir / "results.json").write_text(to_json(run), encoding="utf-8")
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return run_dir
