from __future__ import annotations

import argparse

from .input_packs import write_input_pack


def main() -> None:
    parser = argparse.ArgumentParser(
        description="평가 정답과 부가 메타데이터를 제외한 공개 모델 입력팩을 생성합니다."
    )
    parser.add_argument("--suite", required=True, help="평가용 공개 시나리오 JSON 파일")
    parser.add_argument("--output", required=True, help="생성할 모델 입력팩 JSON 파일")
    args = parser.parse_args()

    output = write_input_pack(args.suite, args.output)
    print(f"공개 모델 입력팩: {output}")


if __name__ == "__main__":
    main()
