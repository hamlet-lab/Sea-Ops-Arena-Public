# 공개 결과 파일 규칙

SEA Ops Arena는 실제 외부 모델·사람·외부 시스템의 결과를 비교할 수 있도록 **공개 전용 결과 포맷**을 제공합니다.

이 포맷의 목적은 원본 실행 로그를 저장하는 것이 아니라, Arena 평가에 필요한 최소한의 최종 결과와 재현 정보를 남기는 것입니다.

## 기본 원칙

현재 `public-decision-set-v1`은 허용 필드만 저장하는 화이트리스트 방식입니다.

허용되는 최상위 필드:

- `schema_version`
- `label`
- `suite_sha256`
- `input_pack_sha256`
- `source`
- `decisions`

`source`에서 허용되는 필드:

- `kind`
- `model_name`
- `model_version`
- `recorded_at`
- `repeat_id`

이 목록에 없는 필드가 들어오면 로더가 실행 전에 오류를 발생시킵니다.

## 실제 결과에는 두 개의 결합 해시가 필요합니다

`fixture`가 아닌 실제 외부 결과에는 다음 두 값이 모두 필요합니다.

### `suite_sha256`

평가에 사용되는 **정확한 평가용 시나리오 JSON 파일**의 SHA-256입니다.

Arena는 결과 파일의 `suite_sha256`과 현재 평가하려는 시나리오 파일을 비교합니다. 둘이 다르면 평가를 중단합니다.

### `input_pack_sha256`

판단 생성 대상이 실제로 본 **정답 비노출 입력팩**의 SHA-256입니다.

실제 결과를 평가할 때는 해당 입력팩 파일도 함께 제공해야 합니다.

Arena는 다음을 확인합니다.

1. 입력팩의 `source_suite.sha256`이 평가용 시나리오와 일치하는가
2. 결과의 `input_pack_sha256`이 제공된 입력팩 파일과 일치하는가

하나라도 다르면 평가를 중단합니다.

이 결합은 다음과 같은 실수를 막기 위한 것입니다.

- 정답이 포함된 평가 파일을 모델 입력으로 사용
- 다른 버전의 입력을 본 결과를 같은 실험으로 취급
- 시나리오 수정 이후 예전 결과를 새 기준으로 평가
- 반복 실행 사이에 입력팩이 바뀌었는데 같은 실험으로 표시

정답 비노출 입력 절차는 [`BLIND_EVALUATION.md`](BLIND_EVALUATION.md)를 참고해 주세요.

## fixture와 실제 결과의 차이

저장소에 포함된 합성 fixture는 Arena 기능을 빠르게 보여 주기 위한 예시이므로 결합 해시를 생략할 수 있습니다.

반면 다음 `source.kind`는 실제 외부 결과로 취급하며 두 해시 결합을 요구합니다.

- `model`
- `human`
- `external-system`

## 저장하지 않는 정보

공개 결과 파일에는 다음을 넣지 않습니다.

- 비공개 프롬프트
- 시스템 메시지
- 원본 응답 전문
- 내부 추론 또는 작업 로그
- 내부 상태·정책·구조 정보
- API 키나 인증 토큰
- 내부 URL 및 파일 경로
- 공개 검토를 거치지 않은 임의 metadata

새 정보가 필요해져도 임의 필드를 바로 추가하지 않습니다. 공개 필요성과 유출 가능성을 검토한 뒤 포맷 버전을 올려 명시적으로 추가합니다.

## 예시

```json
{
  "schema_version": "public-decision-set-v1",
  "label": "example-run",
  "suite_sha256": "<평가용 시나리오 파일 SHA-256>",
  "input_pack_sha256": "<정답 비노출 입력팩 SHA-256>",
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

## 권장 생성 방법

원본 로그에서 공개할 부분을 삭제하며 결과 파일을 만드는 방식보다, 먼저 안전한 빈 템플릿을 생성하는 방식을 권장합니다.

### 1. 입력팩 생성

```bash
sea-ops-arena-input-pack \
  --suite examples/scenarios/public_suite_v2.json \
  --output model-input.json
```

### 2. 결과 템플릿 생성

```bash
sea-ops-arena-template \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --output model-run-001.public.json \
  --label example-run \
  --kind model \
  --model-name public-model-name \
  --model-version public-version \
  --repeat-id run-001
```

템플릿의 `decisions`에 있는 `__FILL__` 값만 최종 `proceed`, `reject`, `defer`로 채웁니다.

## 평가

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --decisions model-run-001.public.json
```

실제 외부 결과에서 `--input-pack`을 빼면 평가를 거부합니다.

## 반복 결과

같은 대상의 반복 실험은 반복마다 별도 공개 결과 파일로 남깁니다.

각 파일에는 서로 다른 `source.repeat_id`를 사용합니다. 반복 평가 시 다음 정보가 일치해야 합니다.

- `label`
- `source.kind`
- `source.model_name`
- `source.model_version`
- 평가용 시나리오
- 정답 비노출 입력팩

Arena는 공개된 최종 판단의 반복 변동만 계산합니다. 내부 사고 과정이나 비공개 상태의 일관성을 요구하거나 공개하지 않습니다.

## 공개 저장소에 실제 결과를 넣을 때

실제 외부 결과가 공개 저장소에 포함되면 그 결과가 참조하는 정답 비노출 입력팩도 함께 공개하는 것을 기본으로 합니다.

`sea-ops-arena-audit --root .`은 실제 결과가 가리키는 입력팩 해시와 일치하는 입력팩 파일이 저장소에 존재하는지 확인합니다.

자동 감사가 통과해도 의미적 기술 유출 여부가 자동으로 보장되는 것은 아닙니다. 내부 명칭 검사와 여러 파일을 조합한 역추론 가능성 검토는 별도로 유지합니다.

## 기존 예제와의 관계

- `examples/decisions/` — 빠른 데모용 단순 fixture
- `examples/results/` — 엄격 공개 결과 포맷과 반복 평가를 보여 주는 fixture

이 예제들은 실제 모델 또는 SEA 성능을 주장하는 자료가 아닙니다.
