# 정답 비노출 외부 평가

SEA Ops Arena의 평가용 공개 시나리오에는 계산을 재현하기 위한 기대 판단이 포함될 수 있습니다. 따라서 **실제 모델·사람·외부 시스템의 판단을 생성할 때 평가용 시나리오 JSON을 그대로 입력으로 사용하면 안 됩니다.**

## 평가 파일과 모델 입력의 분리

### 평가용 시나리오

예: `examples/scenarios/public_suite_v2.json`

이 파일은 Arena가 결과를 채점하고 외부에서 계산 방법을 재현하기 위한 파일입니다. 공개 기대 판단, 평가 태그 등 평가 전용 정보가 포함될 수 있습니다.

### 정답 비노출 입력팩 v2

`arena-input-pack-v2`는 판단 생성 대상이 실제로 보는 별도 파일입니다.

포함되는 정보:

- 사례 식별자와 설명
- 공개 실행 요청
- 원본 시나리오 ID와 SHA-256
- 공개 과제 정의
- `proceed` / `reject` / `defer`의 공개 의미
- 필요한 request ID 목록과 출력 계약
- 첫 baseline의 실행 제약

고정 실행 제약:

- `use_only_input_pack_content`
- `no_external_tools_or_retrieval`
- `return_final_status_map_only`

포함되지 않는 정보:

- `expected_decision`
- 실행 결과 기대값
- `tags`
- 평가 메모
- 임의 metadata
- 외부 context 참조
- 비공개 프롬프트나 시스템 메시지
- 내부 로그 또는 trace

입력팩 v2는 의도적으로 **자기완결적인 공개 요청과 공개 benchmark 과제만** 허용합니다.

## 1. 입력팩 생성

```bash
sea-ops-arena-input-pack \
  --suite examples/scenarios/public_suite_v2.json \
  --output model-input.json
```

생성기는 원본 JSON을 복사해 일부 키를 지우는 방식이 아니라, 허용된 공개 필드만 새 객체에 다시 작성합니다.

## 2. 판단 생성

모델·사람·외부 시스템에는 **`model-input.json`만 제공합니다.**

입력팩 안에 과제와 출력 계약이 함께 들어 있으므로 외부에서 별도의 비공개 판단 규칙을 주입하지 않습니다. 첫 baseline에서는 웹검색, RAG, 외부 도구를 사용하지 않습니다.

모델 호출 또는 비공개 시스템 실행은 별도 환경에서 수행하고, 공개 단계에는 request ID별 최종 상태만 가져옵니다.

첫 실제 baseline의 반복 조건은 [`BASELINE_PROTOCOL.md`](BASELINE_PROTOCOL.md)를 따릅니다.

## 3. 안전한 결과 템플릿 생성

```bash
sea-ops-arena-template \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --output model-run-001.public.json \
  --label example-model \
  --kind model \
  --model-name public-model-name \
  --model-version public-version \
  --repeat-id run-001
```

템플릿에는 다음 두 해시가 기록됩니다.

- `suite_sha256`: 평가에 사용하는 정확한 시나리오 파일
- `input_pack_sha256`: 판단 생성 대상이 실제로 본 입력팩 전체

`input_pack_sha256`은 사례뿐 아니라 공개 과제 정의와 실행 제약까지 함께 고정합니다.

`decisions`의 `__FILL__` 값만 `proceed`, `reject`, `defer` 중 하나로 채웁니다. 원본 응답 전문, 추론 과정, 로그를 복사하지 않습니다.

## 4. 평가

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --decisions model-run-001.public.json
```

Arena는 다음을 확인합니다.

1. 결과의 `suite_sha256`이 평가 시나리오와 일치하는가
2. 입력팩의 `source_suite.sha256`이 평가 시나리오와 일치하는가
3. 입력팩의 과제·출력 계약·실행 제약이 표준 v2 계약과 일치하는가
4. 결과의 `input_pack_sha256`이 제공된 입력팩과 일치하는가
5. 모든 request ID 결과가 존재하는가

하나라도 일치하지 않으면 평가를 거부합니다.

## 5. 비교와 반복 평가

실제 결과 비교와 반복 평가에도 동일한 입력팩을 명시합니다.

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

## 6. 공개 전 감사

실제 결과를 공개 저장소에 추가한다면 참조하는 정답 비노출 입력팩도 함께 공개하는 것을 기본으로 합니다.

```bash
sea-ops-arena-audit --root .
```

자동 감사와 별도로 내부 명칭 검사 및 여러 공개 파일을 조합한 의미 단위 역추론 검토를 수행합니다.

## 왜 이렇게 분리하나

정답 공개는 평가 계산을 투명하게 만드는 데 유리하지만, 같은 파일을 판단 생성 대상에게 제공하면 실험이 오염됩니다.

SEA Ops Arena는 **평가 기준의 공개 가능성**과 **판단 생성 시 정답 비노출**을 파일 수준에서 분리합니다. 이 장치는 SEA 또는 다른 연결 시스템의 내부 구현을 공개하기 위한 것이 아닙니다.
