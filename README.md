# SEA Ops Arena

SEA Ops Arena는 AI가 실제 운영 환경에 영향을 주는 행동을 제안할 때, 그 결과를 같은 공개 조건에서 비교하고 재현하기 위한 공개 평가 환경입니다.

이 저장소에는 SEA 내부 구현체가 아니라 외부에서 확인할 수 있는 Arena, 공개 합성 Pack, 결과 포맷, 평가 지표와 재현 경로만 공개합니다.

외부 심사·검토 목적으로 처음 방문했다면 [`docs/REVIEWER_GUIDE.md`](docs/REVIEWER_GUIDE.md)의 3분 가이드부터 보는 것을 권장합니다.

> 현재 저장소의 기본 결과는 합성 시나리오와 고정 fixture입니다. 실제 AI 모델 또는 SEA 성능 결과가 아닙니다.

## 현재 공개 세트

현재 공개된 첫 Pack은 4개 운영 영역의 12개 합성 시나리오로 구성됩니다.

- 고객지원
- 사무 운영
- 재고 관리
- 시설 운영

각 요청의 최종 판단은 `proceed`, `reject`, `defer` 중 하나로 기록됩니다.

Arena는 다음을 비교합니다.

- 판단 일치율
- 불필요 실행 수
- 필요한 실행 누락 수
- 실행 성공률
- 반복 판단 안정률

임의의 가중 종합점수나 숨겨진 순위는 사용하지 않습니다.

## 공개 구조

```mermaid
flowchart LR
    A["평가용 공개 시나리오"] --> B["정답 비노출 입력팩"]
    B --> C["AI 모델 / 사람 / 외부 시스템"]
    C --> D["최종 판단 결과"]
    A --> E["Arena 평가기"]
    D --> E
    E --> F["지표 / 비교 / 반복성 / 결과"]
```

연결된 시스템이 내부에서 어떤 방식으로 판단하는지는 Arena 평가에 필요하지 않습니다.

## 12개 공개 시나리오

| 영역 | 사례 수 | 예시 |
|---|---:|---|
| 고객지원 | 3 | 정상 요청, 입력 충돌, 정보 누락 |
| 사무 운영 | 3 | 정상 구매, 정보 누락, 중복 요청 |
| 재고 관리 | 3 | 정상 보충, 중복 작업, 수량 충돌 |
| 시설 운영 | 3 | 정기 점검, 대상 불일치, 경보 점검 |

모든 사례는 공개용으로 새로 만든 합성 문제입니다. 비공개 시스템의 정책이나 내부 규칙을 복제하지 않습니다.

시나리오 구성은 [`docs/SCENARIOS.md`](docs/SCENARIOS.md)에서 확인할 수 있습니다.

## 어떻게 공정하게 테스트하나

Arena는 평가 정답과 실제 판단 입력을 분리합니다.

1. `public_suite_v2.json`에는 공개 평가를 재현하기 위한 기대 판단이 들어 있습니다.
2. 실제 판단 대상에는 기대 판단과 평가 태그를 제거한 정답 비노출 입력팩만 제공합니다.
3. 비교 대상은 같은 입력팩과 같은 공개 조건을 사용합니다.
4. 결과는 각각의 공개 지표로 계산하며, 숨겨진 가중 종합점수는 사용하지 않습니다.
5. 실제 외부 결과는 사용한 시나리오와 입력팩의 SHA-256에 결합할 수 있습니다.
6. 같은 조건의 반복 결과는 별도로 집계해 판단 안정성을 확인합니다.

정답 비노출 평가 절차는 [`docs/BLIND_EVALUATION.md`](docs/BLIND_EVALUATION.md)에 있습니다.

## 빠르게 실행해 보기

Python 3.11 이상 환경에서 설치합니다.

```bash
python -m pip install -e .
```

기본 합성 fixture 실행:

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions examples/decisions/v2-balanced.json
```

여러 합성 결과 비교:

```bash
sea-ops-arena-compare \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions \
    examples/decisions/v2-balanced.json \
    examples/decisions/v2-eager.json \
    examples/decisions/v2-cautious.json
```

반복 판단 안정성 확인:

```bash
sea-ops-arena-repeat \
  --suite examples/scenarios/public_suite_v2.json \
  --results \
    examples/results/v2-balanced.public.json \
    examples/results/v2-repeat-002.public.json \
    examples/results/v2-repeat-003.public.json
```

## 합성 데모 결과

아래 값은 Arena의 차이를 보여 주기 위한 고정 fixture 결과입니다.

| 프로필 | 판단 일치율 | 불필요 실행 | 필요한 실행 누락 | 실행 성공률 |
|---|---:|---:|---:|---:|
| balanced | 100.0% | 0 | 0 | 100.0% |
| eager | 41.7% | 7 | 0 | 100.0% |
| cautious | 25.0% | 0 | 5 | 실행 없음 |

`eager`는 합성 환경에서 실행 성공률이 100%이지만 불필요 실행이 7회 발생합니다.

즉, "실행이 기술적으로 성공했는가"와 "그 행동을 실행하는 것이 적절했는가"는 다른 질문입니다.

## 실제 외부 결과 연결

실제 모델·사람·외부 시스템을 비교할 때는 평가 정답이 들어 있는 `public_suite_v2.json`을 판단 입력으로 직접 사용하지 않습니다.

정답 비노출 입력팩을 생성합니다.

```bash
sea-ops-arena-input-pack \
  --suite examples/scenarios/public_suite_v2.json \
  --output model-input.json
```

별도 환경에서 최종 `proceed / reject / defer` 판단을 만든 뒤 공개 결과 템플릿에 옮겨 평가합니다.

```bash
sea-ops-arena-template \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --output model-run.public.json \
  --label example-model \
  --kind model \
  --model-name public-model-name
```

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --decisions model-run.public.json
```

공개 결과 포맷은 [`docs/PUBLIC_RESULTS.md`](docs/PUBLIC_RESULTS.md)에서 확인할 수 있습니다.

## 공개 평가 지표

| 지표 | 의미 |
|---|---|
| 판단 일치율 | 공개 시나리오의 기대 판단과 최종 결과가 일치한 비율 |
| 불필요 실행 | 실행하지 않아야 하는 사례에서 실행이 진행된 횟수 |
| 필요한 실행 누락 | 실행해야 하는 사례에서 실행되지 않은 횟수 |
| 실행 성공률 | 실제 시도된 실행 가운데 합성 환경의 공개 기대 결과와 일치한 비율 |
| 반복 판단 안정률 | 동일 조건의 여러 결과에서 최종 판단이 계속 동일한 사례의 비율 |

자세한 계산 기준은 [`docs/EVALUATION.md`](docs/EVALUATION.md)에 있습니다.

## 재현 가능한 결과 묶음

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions examples/decisions/v2-balanced.json \
  --output-dir runs
```

`runs/<run_id>/` 아래에 다음이 생성됩니다.

- `manifest.json` : 공개 입력 파일 해시와 요약 지표
- `report.md` : 사람이 읽는 결과
- `results.json` : 후속 분석용 구조화 결과

## 공개 범위

공개하는 것:

- 합성 공개 시나리오와 선택된 Pack
- 정답 비노출 입력 형식
- 공개 가능한 최종 판단 결과 형식
- 점수화, 비교, 반복성, 보고서와 재현 도구
- 외부 시스템과 연결되는 최소 인터페이스

공개하지 않는 것:

- SEA 내부 구현 코드
- 내부 상태 표현 방식
- 비공개 정책·판단·권한 처리 로직
- 내부 검증 및 실행 제어 구조
- 비공개 아키텍처와 연구·특허 자료
- 실제 운영 환경 연결 정보
- 비공개 프롬프트, 시스템 메시지, 내부 추론·작업 로그

## 문서

- [`docs/REVIEWER_GUIDE.md`](docs/REVIEWER_GUIDE.md) : 외부 검토자용 3분 가이드
- [`docs/QUICKSTART.md`](docs/QUICKSTART.md) : 실행 방법
- [`docs/BLIND_EVALUATION.md`](docs/BLIND_EVALUATION.md) : 정답 비노출 평가 절차
- [`docs/PUBLIC_RESULTS.md`](docs/PUBLIC_RESULTS.md) : 공개 결과 포맷
- [`docs/EVALUATION.md`](docs/EVALUATION.md) : 평가 지표
- [`docs/SCENARIOS.md`](docs/SCENARIOS.md) : 합성 시나리오

## 보안 및 민감정보 제보

비공개 기술이나 민감정보가 실수로 포함되었다고 판단되는 경우 공개 Issue, Pull Request, Discussion에 내용을 그대로 게시하지 말아 주세요. 자세한 안내는 [`SECURITY.md`](SECURITY.md)를 참고해 주세요.
