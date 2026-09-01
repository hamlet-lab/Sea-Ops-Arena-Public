# 공개 결과 파일 규칙

SEA Ops Arena는 실제 외부 모델·에이전트·사람·외부 시스템의 결과를 나중에 비교할 수 있도록 **공개 전용 결과 포맷**을 제공합니다.

이 포맷의 목적은 원본 실행 로그를 그대로 저장하는 것이 아니라, Arena 평가에 필요한 최소 결과만 남기는 것입니다.

## 기본 원칙

공개 결과 파일은 **허용된 필드만 저장하는 방식**을 사용합니다.

현재 `public-decision-set-v1`에서 허용하는 최상위 필드는 다음 네 가지뿐입니다.

- `schema_version`
- `label`
- `source`
- `decisions`

`source` 역시 다음 필드만 허용합니다.

- `kind`
- `model_name`
- `model_version`
- `recorded_at`
- `repeat_id`

이 목록에 없는 필드가 들어오면 로더가 실행 전에 오류를 발생시킵니다.

## 저장하지 않는 정보

공개 결과 파일에는 다음과 같은 원본 실행 정보를 넣지 않습니다.

- 비공개 프롬프트
- 시스템 메시지
- 내부 추론 또는 작업 로그
- 내부 상태·정책·구조 정보
- API 키나 인증 토큰
- 내부 URL 및 파일 경로
- 공개 검토를 거치지 않은 임의 metadata

필요한 정보가 생기면 임의 필드를 바로 추가하지 않고, 공개 필요성과 유출 가능성을 검토한 뒤 포맷 버전을 올려 명시적으로 추가합니다.

## 예시

```json
{
  "schema_version": "public-decision-set-v1",
  "label": "example-run",
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

실제 실행 가능한 합성 예시는 `examples/results/v2-balanced.public.json`에 있습니다.

## 지원하는 출처 종류

현재 `source.kind`는 다음 네 종류만 허용합니다.

- `fixture`: 저장소에 포함된 합성 고정 예시
- `model`: 공개 모델 결과
- `human`: 사람의 공개 판단 결과
- `external-system`: 기타 외부 시스템의 공개 결과

이 값은 결과의 출처를 구분하기 위한 공개 메타데이터일 뿐, 연결된 시스템의 내부 구조를 나타내지 않습니다.

## 기존 예제와의 관계

`examples/decisions/` 아래의 단순 JSON 파일은 Arena 동작을 빠르게 보여 주기 위한 기존 합성 fixture 형식입니다.

실제 외부 결과를 저장하거나 장기적으로 배포할 때는 허용 필드가 제한된 `public-decision-set-v1` 사용을 권장합니다.
