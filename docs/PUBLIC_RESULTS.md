# 공개 결과 파일 규칙

SEA Ops Arena는 실제 외부 모델·사람·외부 시스템의 결과를 같은 형식으로 비교할 수 있도록 공개 결과 포맷을 제공합니다.

현재 포맷은 `public-decision-set-v1`입니다.

## 필드

최상위 필드:

- `schema_version`
- `label`
- `suite_sha256`
- `input_pack_sha256`
- `source`
- `decisions`

`source` 필드:

- `kind`
- `model_name`
- `model_version`
- `recorded_at`
- `repeat_id`

허용되지 않은 필드는 로더가 거부합니다.

## 입력 결합

실제 외부 결과는 평가 시나리오와 정답 비노출 입력팩을 SHA-256으로 식별합니다.

- `suite_sha256` : 평가에 사용한 시나리오 파일
- `input_pack_sha256` : 판단 대상이 본 정답 비노출 입력팩

Arena는 평가 전에 두 파일과 결과의 결합이 일치하는지 확인합니다.

## 예시

```json
{
  "schema_version": "public-decision-set-v1",
  "label": "example-run",
  "suite_sha256": "<scenario sha256>",
  "input_pack_sha256": "<input pack sha256>",
  "source": {
    "kind": "model",
    "model_name": "public-model-name",
    "model_version": "public-version",
    "repeat_id": "run-001"
  },
  "decisions": {
    "request-001": "proceed",
    "request-002": "reject",
    "request-003": "defer"
  }
}
```

## 결과 템플릿 생성

```bash
sea-ops-arena-template \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --output model-run.public.json \
  --label example-run \
  --kind model \
  --model-name public-model-name
```

템플릿의 `decisions`에 있는 `__FILL__` 값을 최종 `proceed`, `reject`, `defer`로 채웁니다.

## 평가

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --decisions model-run.public.json
```

## 반복 결과

같은 대상의 반복 실행은 각각 별도 결과 파일로 저장합니다. 반복마다 다른 `source.repeat_id`를 사용합니다.

반복 평가 시 모델명, 모델 버전, 시나리오와 입력팩이 같은지 확인한 뒤 최종 판단의 안정성을 집계합니다.

## 저장하지 않는 정보

공개 결과 파일에는 다음을 넣지 않습니다.

- 비공개 프롬프트
- 시스템 메시지
- 원본 응답 전문
- 내부 추론 또는 작업 로그
- API 키나 인증 토큰
- 실제 운영 환경의 내부 URL과 파일 경로

## 기존 예제

- `examples/decisions/` : 빠른 데모용 fixture
- `examples/results/` : 공개 결과 포맷과 반복 평가 예시

현재 예제는 실제 모델 또는 SEA 성능을 주장하는 자료가 아닙니다.
