# 실제 SEA 적용 결과

이 문서는 SEA Ops Arena의 이전 실제 모델 비교 트랙에서 보존된 공개 가능 결과를 정리합니다.

현재 저장소의 `public_suite_v2` 합성 fixture와는 **다른 실험 계보**입니다. 아래 실제 SEA 결과를 v2 fixture 점수와 합산하거나 같은 분모로 비교하면 안 됩니다.

## 대표 실제 모델 비교

3개 로컬 모델을 사용해 모델별 10회 반복한 비교에서 총 120개 비교 행이 기록되었습니다.

| 실행 조건 | 위험 상태 변경 |
|---|---:|
| LLM only | 60 |
| LLM + RAG | 50 |
| LLM + SEA | 0 |
| LLM + RAG + SEA | 0 |

사용된 공개 모델 라벨은 다음과 같습니다.

- `gemma-4-e2b`
- `llama-3.3-70b-instruct`
- `openai/gpt-oss-20b`

이 결과에서 비교한 핵심은 모델 자체의 순위가 아니라 **같은 모델 출력을 어떤 실행 구조에 연결했을 때 외부 결과가 달라지는가**입니다.

## 별도 paired matrix

별도의 `fair_comparison_v1` 매트릭스에는 36개 비교 행이 있습니다. 이 프로토콜에서도 같은 방향의 차이가 기록되었습니다.

| 비교 | SEA 적용 전 | SEA 적용 후 |
|---|---:|---:|
| LLM only → LLM + SEA | 42 | 0 |
| LLM + RAG → LLM + RAG + SEA | 21 | 0 |

이 36개 행은 위 120개 대표 집계와 **별도 프로토콜의 결과**입니다. 두 수치를 하나의 분모처럼 합산하지 않습니다.

## 무엇을 주장할 수 있나

이 공개 증거가 직접 보여 주는 것은 제한적입니다.

- 합성 운영 Arena에서 실제 로컬 모델을 연결한 비교가 수행되었습니다.
- 해당 보존 결과에서 LLM 또는 LLM+RAG 경로에는 위험 상태 변경이 기록되었습니다.
- 같은 비교군에 SEA를 적용한 경로에서는 해당 지표가 0건으로 기록되었습니다.
- 따라서 이 실험 범위에서는 모델 자체뿐 아니라 **실행 구조의 차이**가 외부 결과에 영향을 주었습니다.

## 무엇을 주장하지 않나

이 결과는 다음을 의미하지 않습니다.

- 실제 산업 현장의 안전 인증
- 모든 환경에서 위험 행동을 100% 막는다는 보증
- 특정 LLM의 우열을 증명하는 모델 벤치마크
- 현재 `public_suite_v2`의 blind baseline 결과
- SEA 내부 알고리즘이나 정책 구조의 공개

## 공개 경계

복원된 공개 데이터에는 다음을 포함하지 않습니다.

- raw model output
- system prompt 또는 private prompt
- 내부 실행 trace/log
- SEA 내부 상태 표현
- 내부 정책, 권한, 검증 또는 실행 제어 구조
- SEA core 구현 코드

공개 데이터는 외부에서 확인 가능한 집계 결과와 공개 모델 라벨만 유지합니다.

구조화된 요약은 [`../evidence/sea_actual_headline_v1.json`](../evidence/sea_actual_headline_v1.json)에서 확인할 수 있습니다.

## 현재 v2 Arena와의 관계

현재 12개 `public_suite_v2`는 공개 재현성과 blind evaluation을 강화하기 위해 새로 만든 평가 표면입니다.

따라서 저장소에는 두 종류의 결과가 공존합니다.

1. **Preserved actual SEA evidence** — 실제 모델과 SEA를 연결했던 이전 Arena 실험 결과
2. **Current public v2 fixtures / future blind results** — 현재 공개 평가기와 입력팩을 검증하고 앞으로 동일 조건의 외부 결과를 받기 위한 트랙

fixture는 실제 SEA 결과를 대체하지 않습니다. 반대로 이전 실제 SEA 결과도 현재 v2의 blind baseline으로 가장하지 않습니다.
