from __future__ import annotations

import argparse

from .template import write_public_result_template


def main() -> None:
    parser = argparse.ArgumentParser(
        description="공개 시나리오에 결합된 최소 결과 템플릿을 생성합니다."
    )
    parser.add_argument("--suite", required=True, help="공개 시나리오 JSON 파일")
    parser.add_argument("--output", required=True, help="생성할 공개 결과 템플릿 JSON")
    parser.add_argument("--label", required=True, help="외부에 공개할 결과 묶음 이름")
    parser.add_argument(
        "--kind",
        required=True,
        choices=("fixture", "model", "human", "external-system"),
        help="공개 결과 출처 유형",
    )
    parser.add_argument("--model-name", help="공개 가능한 모델 이름")
    parser.add_argument("--model-version", help="공개 가능한 모델 버전")
    parser.add_argument("--recorded-at", help="공개 가능한 기록 시각")
    parser.add_argument("--repeat-id", help="반복 실험 식별자")
    args = parser.parse_args()

    path = write_public_result_template(
        args.suite,
        args.output,
        label=args.label,
        kind=args.kind,
        model_name=args.model_name,
        model_version=args.model_version,
        recorded_at=args.recorded_at,
        repeat_id=args.repeat_id,
    )
    print(f"공개 결과 템플릿: {path}")
    print("각 __FILL__ 값을 proceed, reject, defer 중 하나로 검토해 채운 뒤 사용하세요.")


if __name__ == "__main__":
    main()
