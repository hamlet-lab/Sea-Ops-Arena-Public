# 빠른 실행

이 저장소의 공개 예시는 외부 API 키나 실제 운영 시스템 없이 실행할 수 있습니다.

## 설치

Python 3.11 이상을 권장합니다.

```bash
python -m pip install -e .
```

## 1. 12개 공개 합성 시나리오 실행

현재 대표 공개 세트는 `public_suite_v2.json`입니다.

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions examples/decisions/v2-balanced.json
```

`v2-balanced`는 공개 기대값과 동일하게 준비한 고정 예시이며 실제 모델 또는 SEA 성능이 아닙니다.

## 2. 여러 결과를 한 번에 비교

같은 시나리오에 여러 판단 결과 파일을 적용하고 공개 지표를 한 표에서 비교할 수 있습니다.

```bash
sea-ops-arena-compare \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions \
    examples/decisions/v2-balanced.json \
    examples/decisions/v2-eager.json \
    examples/decisions/v2-cautious.json
```

비교 도구는 임의의 가중 종합점수나 순위를 만들지 않고 다음 관찰값을 나란히 보여 줍니다.

- 판단 일치율
- 불필요 실행
- 필요한 실행 누락
- 실행 성공률

결과 예시는 [`../examples/V2_COMPARISON.md`](../examples/V2_COMPARISON.md)를 참고해 주세요.

## 3. 반복 결과의 안정성 평가

같은 출처·같은 모델 버전의 엄격 공개 결과를 여러 번 기록했다면 반복 안정성을 별도로 볼 수 있습니다.

```bash
sea-ops-arena-repeat \
  --suite examples/scenarios/public_suite_v2.json \
  --results \
    examples/results/v2-balanced.public.json \
    examples/results/v2-repeat-002.public.json \
    examples/results/v2-repeat-003.public.json
```

반복 평가에서는 다음을 보여 줍니다.

- 반복별 판단 일치율
- 반복별 불필요 실행
- 반복별 필요한 실행 누락
- 판단 일치율 평균과 범위
- 모든 반복에서 같은 최종 판단을 낸 사례 수
- 반복 판단 안정률

반복 판단 안정률은 **공개된 최종 판단의 반복 일관성**만 의미합니다. 내부 추론이나 비공개 상태를 측정하지 않습니다.

## 4. 실제 외부 결과용 안전한 템플릿 만들기

실제 외부 모델·사람·외부 시스템 결과를 공개할 때는 원본 로그를 복사해서 지우는 방식보다, 먼저 허용 필드만 가진 템플릿을 만드는 방식을 권장합니다.

```bash
sea-ops-arena-template \
  --suite examples/scenarios/public_suite_v2.json \
  --output public-result.json \
  --label example-model-run \
  --kind model \
  --model-name public-model-name \
  --model-version public-version \
  --repeat-id run-001
```

생성된 파일에는 다음만 들어갑니다.

- 공개 결과 스키마 버전
- 공개 라벨
- 정확한 시나리오 파일의 SHA-256
- 공개 가능한 최소 출처 정보
- 시나리오의 request ID 목록
- 각 판단을 채울 `__FILL__` 자리

`__FILL__`은 유효한 판단값이 아니므로 그대로는 평가되지 않습니다. 검토 후 각 값을 `proceed`, `reject`, `defer` 중 하나로 채웁니다.

이 방식은 원본 프롬프트·시스템 메시지·내부 로그를 공개 파일에 복사하지 않도록 작업 흐름 자체를 제한하기 위한 것입니다.

## 5. 외부 결과용 엄격 공개 포맷

실제 외부 결과는 `public-decision-set-v1` 형식을 사용합니다.

최상위 허용 필드는 다음뿐입니다.

- `schema_version`
- `label`
- `suite_sha256`
- `source`
- `decisions`

실제 모델·사람·외부 시스템 결과는 `suite_sha256`이 필수입니다. 현재 시나리오 파일의 SHA-256과 다르면 Arena가 평가를 거부합니다.

저장소의 합성 예시는 다음처럼 실행할 수 있습니다.

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions examples/results/v2-balanced.public.json
```

허용되지 않은 임의 필드가 들어오면 실행 전에 오류가 발생합니다. 상세 규칙은 [`PUBLIC_RESULTS.md`](PUBLIC_RESULTS.md)를 참고해 주세요.

## 6. 재현 가능한 실행 결과 묶음 저장

`--output-dir`을 지정하면 입력 파일의 SHA-256 해시와 결과를 함께 저장합니다.

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions examples/decisions/v2-balanced.json \
  --output-dir runs
```

`runs/<run_id>/` 아래에 다음 세 파일이 생성됩니다.

- `manifest.json`: 공개 입력 파일명, SHA-256 해시, 실행 식별자, 요약 지표
- `report.md`: 사람이 읽기 쉬운 한국어 결과 보고서
- `results.json`: 후속 분석에 사용할 수 있는 구조화 결과

`run_id`는 공개 시나리오 파일과 판단 결과 파일의 해시로 결정됩니다. 같은 두 입력 파일을 사용하면 같은 실행 식별자를 얻습니다.

manifest에는 호스트명, 환경변수, 내부 시스템 경로, 비공개 판단 과정 같은 정보가 포함되지 않습니다.

## 7. JSON 결과를 표준 출력으로 보기

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions examples/decisions/v2-balanced.json \
  --format json
```

## 8. 작은 v1 데모

처음 구조를 빠르게 살펴보고 싶다면 기존 3개 사례 데모도 유지합니다.

```bash
python -m sea_ops_arena.demo
```

또는:

```bash
sea-ops-arena \
  --suite examples/scenarios/public_demo_v1.json \
  --decisions examples/decisions/balanced.json
```

## 9. 테스트

```bash
python -m pytest
```

테스트는 공개 하네스, 공개 입출력, 공개 지표, 결과 비교, 반복 안정성, 공개 결과 포맷, 시나리오 해시 결합, 결과 템플릿과 재현용 결과 묶음만 검증합니다. 비공개 의사결정 시스템의 내부 규칙이나 구조를 검증하지 않습니다.

GitHub Actions에서는 테스트뿐 아니라 주요 CLI 실행 경로도 함께 확인합니다.

## 결과를 볼 때 주의할 점

현재 저장소에 포함된 기본 결과는 **합성 시나리오 + 고정 응답**입니다. 따라서 여기서 나오는 수치를 실제 SEA 성능, 실제 AI 모델 성능 또는 산업 현장 성능으로 해석하면 안 됩니다.

공개 시나리오의 작성 원칙은 [`SCENARIOS.md`](SCENARIOS.md)를 참고해 주세요. 실제 비교 결과가 추가될 경우에는 공개 가능한 출처 정보와 정확한 시나리오 파일 결합 정보를 함께 표시합니다.
