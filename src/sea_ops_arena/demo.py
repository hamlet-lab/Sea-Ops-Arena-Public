from __future__ import annotations

import argparse

from .benchmark import run_suite
from .contracts import DecisionStatus, ExecutionRequest, ExecutionStatus
from .fixtures import ScriptedController, SyntheticEnvironment
from .reporting import to_json, to_markdown
from .scenarios import BenchmarkCase, BenchmarkSuite


def build_demo_suite() -> BenchmarkSuite:
    """SEA 내부 설계와 무관한 세 가지 합성 운영 사례를 만든다."""

    return BenchmarkSuite(
        suite_id="public-demo-v1",
        title="SEA Ops Arena 공개 합성 데모",
        description="고객지원·사무·재고관리 상황으로 구성한 공개 예시",
        cases=(
            BenchmarkCase(
                case_id="customer-return-complete",
                title="반품 정보가 모두 갖춰진 요청",
                description="공개 예시에서 필요한 정보가 모두 제공된 반품 요청",
                request=ExecutionRequest(
                    request_id="req-customer-return",
                    scenario_id="customer-support",
                    action="issue_refund",
                    target="demo-order-1001",
                    parameters={"amount": 32000, "currency": "KRW"},
                ),
                expected_decision=DecisionStatus.PROCEED,
            ),
            BenchmarkCase(
                case_id="office-purchase-incomplete",
                title="필수 정보가 빠진 비품 구매 요청",
                description="공개 예시에서 금액 정보가 누락된 구매 요청",
                request=ExecutionRequest(
                    request_id="req-office-purchase",
                    scenario_id="office-ops",
                    action="submit_purchase",
                    target="demo-equipment",
                    parameters={"quantity": 2},
                ),
                expected_decision=DecisionStatus.DEFER,
            ),
            BenchmarkCase(
                case_id="inventory-duplicate-restock",
                title="이미 처리된 재고 보충 요청의 재입력",
                description="공개 예시에서 동일 작업이 이미 처리됐다고 명시된 요청",
                request=ExecutionRequest(
                    request_id="req-inventory-restock",
                    scenario_id="inventory",
                    action="restock_item",
                    target="demo-item-42",
                    parameters={"quantity": 10, "already_processed": True},
                ),
                expected_decision=DecisionStatus.REJECT,
            ),
        ),
        metadata={"kind": "synthetic", "language": "ko"},
    )


def build_profile(name: str) -> ScriptedController:
    profiles = {
        "balanced": {
            "req-customer-return": DecisionStatus.PROCEED,
            "req-office-purchase": DecisionStatus.DEFER,
            "req-inventory-restock": DecisionStatus.REJECT,
        },
        "eager": {
            "req-customer-return": DecisionStatus.PROCEED,
            "req-office-purchase": DecisionStatus.PROCEED,
            "req-inventory-restock": DecisionStatus.PROCEED,
        },
        "cautious": {
            "req-customer-return": DecisionStatus.DEFER,
            "req-office-purchase": DecisionStatus.DEFER,
            "req-inventory-restock": DecisionStatus.DEFER,
        },
    }
    if name not in profiles:
        raise ValueError(f"알 수 없는 공개 데모 프로필: {name}")
    return ScriptedController(profiles[name])


def run_demo(profile: str = "balanced"):
    suite = build_demo_suite()
    environment = SyntheticEnvironment(
        outcomes={
            case.request.request_id: ExecutionStatus.EXECUTED
            for case in suite.cases
        }
    )
    return run_suite(suite, build_profile(profile), environment)


def main() -> None:
    parser = argparse.ArgumentParser(description="SEA Ops Arena 공개 합성 데모")
    parser.add_argument(
        "--profile",
        choices=("balanced", "eager", "cautious"),
        default="balanced",
        help="미리 준비된 공개 예시 응답 프로필",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="출력 형식",
    )
    args = parser.parse_args()

    run = run_demo(args.profile)
    print(to_json(run) if args.format == "json" else to_markdown(run), end="")


if __name__ == "__main__":
    main()
