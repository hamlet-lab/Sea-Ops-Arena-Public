from __future__ import annotations

import argparse

from .repetitions import evaluate_repeated_results, repeat_evaluation_to_markdown


def main() -> None:
    parser = argparse.ArgumentParser(
        description="동일 출처의 여러 공개 결과 파일을 반복 실험으로 집계합니다."
    )
    parser.add_argument("--suite", required=True, help="평가용 공개 시나리오 JSON 파일")
    parser.add_argument(
        "--input-pack",
        help="실제 외부 결과가 생성될 때 사용된 정답 비노출 입력팩",
    )
    parser.add_argument(
        "--results",
        required=True,
        nargs="+",
        help="둘 이상의 엄격 공개 결과 JSON 파일",
    )
    args = parser.parse_args()

    evaluation = evaluate_repeated_results(args.suite, args.results, args.input_pack)
    print(repeat_evaluation_to_markdown(evaluation), end="")


if __name__ == "__main__":
    main()
