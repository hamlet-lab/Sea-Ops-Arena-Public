# 빠른 실행

이 저장소의 공개 예시는 외부 API 키나 실제 운영 시스템 없이 실행할 수 있습니다.

## 설치

Python 3.11 이상을 권장합니다.

```bash
python -m pip install -e .
```

## 1. 합성 fixture 실행

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions examples/decisions/v2-balanced.json
```

`v2-balanced`는 Arena 동작을 확인하기 위한 고정 예시이며 실제 모델 또는 SEA 성능이 아닙니다.

## 2. 여러 결과 비교

```bash
sea-ops-arena-compare \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions \
    examples/decisions/v2-balanced.json \
    examples/decisions/v2-eager.json \
    examples/decisions/v2-cautious.json
```

판단 일치율, 불필요 실행, 필요한 실행 누락, 실행 성공률을 나란히 확인합니다.

## 3. 반복 안정성 확인

```bash
sea-ops-arena-repeat \
  --suite examples/scenarios/public_suite_v2.json \
  --results \
    examples/results/v2-balanced.public.json \
    examples/results/v2-repeat-002.public.json \
    examples/results/v2-repeat-003.public.json
```

## 실제 외부 결과 연결

### 4. 정답 비노출 입력팩 생성

```bash
sea-ops-arena-input-pack \
  --suite examples/scenarios/public_suite_v2.json \
  --output model-input.json
```

판단 생성 대상에는 `model-input.json`을 제공합니다.

### 5. 결과 템플릿 생성

```bash
sea-ops-arena-template \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --output model-run.public.json \
  --label example-model \
  --kind model \
  --model-name public-model-name
```

### 6. 결과 평가

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --decisions model-run.public.json
```

### 7. 여러 실제 결과 비교

```bash
sea-ops-arena-compare \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --decisions model-a.public.json model-b.public.json
```

### 8. 반복 결과 평가

```bash
sea-ops-arena-repeat \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --results run-001.public.json run-002.public.json run-003.public.json
```

## 재현 가능한 결과 묶음

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions examples/decisions/v2-balanced.json \
  --output-dir runs
```

`runs/<run_id>/` 아래에 `manifest.json`, `report.md`, `results.json`이 생성됩니다.

## 테스트

```bash
python -m pytest
```

## 더 자세히 보기

- [`BLIND_EVALUATION.md`](BLIND_EVALUATION.md) : 정답 비노출 평가 절차
- [`PUBLIC_RESULTS.md`](PUBLIC_RESULTS.md) : 결과 파일 규칙
- [`EVALUATION.md`](EVALUATION.md) : 평가 지표
