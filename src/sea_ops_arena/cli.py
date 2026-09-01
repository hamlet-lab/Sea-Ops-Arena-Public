from __future__ import annotations

import argparse

from .benchmark import run_suite
from .fixtures import ScriptedController, SyntheticEnvironment
from .io import load_decisions, load_suite
from .reporting import to_json, to_markdown


def main() -> None:
    parser = argparse.ArgumentParser(
        description="공개 시나리오와 공개 판단 결과 파일을 SEA Ops Arena에서 실행합니다."
    )
    parser.add_argument("--suite", required=True, help="공개 시나리오 JSON 파일")
    parser.add_argument("--decisions", required=True, help="요청별 공개 판단 결과 JSON 파일")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="출력 형식",
    )
    args = parser.parse_args()

    suite = load_suite(args.suite)
    decisions = load_decisions(args.decisions)
    environment = SyntheticEnvironment(
        outcomes={case.request.request_id: case.environment_status for case in suite.cases}
    )
    run = run_suite(suite, ScriptedController(decisions), environment)
    print(to_json(run) if args.format == "json" else to_markdown(run), end="")


if __name__ == "__main__":
    main()
