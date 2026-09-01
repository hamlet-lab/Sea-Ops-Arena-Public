from __future__ import annotations

import argparse

from .audit import audit_repository


def main() -> None:
    parser = argparse.ArgumentParser(
        description="일반적인 공개 저장소 위험 신호와 공개 결과 포맷을 검사합니다."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="검사할 공개 저장소 루트 경로",
    )
    args = parser.parse_args()

    findings = audit_repository(args.root)
    if not findings:
        print("공개 릴리스 감사: 이상 없음")
        return

    print(f"공개 릴리스 감사: {len(findings)}개 항목 발견")
    for finding in findings:
        print(f"- [{finding.code}] {finding.path}: {finding.message}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
