from __future__ import annotations

import argparse

from .comparison import compare_decision_files, comparison_to_markdown


def main() -> None:
    parser = argparse.ArgumentParser(
        description="동일한 공개 시나리오에 여러 판단 결과 파일을 적용해 비교합니다."
    )
    parser.add_argument("--suite", required=True, help="평가용 공개 시나리오 JSON 파일")
    parser.add_argument(
        "--input-pack",
        help="실제 외부 결과가 생성될 때 사용된 정답 비노출 입력팩",
    )
    parser.add_argument(
        "--decisions",
        required=True,
        nargs="+",
        help="둘 이상의 공개 판단 결과 JSON 파일",
    )
    args = parser.parse_args()

    rows = compare_decision_files(args.suite, args.decisions, args.input_pack)
    print(comparison_to_markdown(rows), end="")


if __name__ == "__main__":
    main()
