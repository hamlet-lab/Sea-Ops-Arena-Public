# 정답 비노출 외부 평가

SEA Ops Arena의 평가용 시나리오에는 계산을 재현하기 위한 기대 판단이 포함될 수 있습니다. 실제 모델·사람·외부 시스템의 판단을 만들 때는 이 평가 파일을 그대로 입력으로 사용하지 않습니다.

## 평가 파일과 판단 입력 분리

평가용 시나리오:

`examples/scenarios/public_suite_v2.json`

판단 생성용 입력:

`arena-input-pack-v2`

입력팩에는 다음이 포함됩니다.

- 사례 식별자와 설명
- 공개 실행 요청
- 공개 과제 정의
- `proceed / reject / defer` 의미
- 출력 계약

다음 평가 전용 정보는 포함하지 않습니다.

- `expected_decision`
- 평가 태그와 메모
- 실행 기대 결과
- 임의 metadata

## 1. 입력팩 생성

```bash
sea-ops-arena-input-pack \
  --suite examples/scenarios/public_suite_v2.json \
  --output model-input.json
```

## 2. 판단 생성

모델·사람·외부 시스템에는 `model-input.json`을 제공합니다.

공개 결과에는 request ID별 최종 상태만 사용합니다.

```json
{
  "v2-cs-01": "proceed",
  "v2-cs-02": "reject",
  "v2-cs-03": "defer"
}
```

## 3. 결과 템플릿 생성

```bash
sea-ops-arena-template \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --output model-run.public.json \
  --label example-model \
  --kind model \
  --model-name public-model-name
```

결과 파일에는 평가 시나리오와 입력팩을 식별하는 SHA-256이 함께 기록됩니다.

## 4. 평가

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --decisions model-run.public.json
```

Arena는 평가 전에 시나리오, 입력팩, 결과 파일의 결합과 request ID 커버리지를 확인합니다.

## 5. 비교와 반복 평가

```bash
sea-ops-arena-compare \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --decisions model-a.public.json model-b.public.json
```

```bash
sea-ops-arena-repeat \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --results run-001.public.json run-002.public.json run-003.public.json
```

평가 기준은 공개하고, 실제 판단 입력에서는 정답을 분리합니다. 연결된 시스템의 내부 구현은 이 과정에 필요하지 않습니다.
