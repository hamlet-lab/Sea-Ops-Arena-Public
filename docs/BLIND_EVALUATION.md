# 정답 비노출 외부 평가

SEA Ops Arena의 공개 시나리오 파일에는 평가를 재현하기 위한 기대 판단이 포함될 수 있습니다. 따라서 **실제 모델·사람·외부 시스템의 판단을 생성할 때 평가용 시나리오 JSON을 그대로 입력으로 사용하면 안 됩니다.**

이 문서는 평가 기준과 판단 생성 입력을 분리하는 공개 절차를 설명합니다.

## 두 파일의 역할

### 평가용 시나리오

예: `examples/scenarios/public_suite_v2.json`

평가용 시나리오는 다음 정보를 함께 가질 수 있습니다.

- 사례 설명
- 실행 요청
- 공개 기대 판단
- 평가에 필요한 부가 정보
- 분류 태그

이 파일은 **Arena가 결과를 채점하고 외부에서 계산 방법을 재현하기 위한 파일**입니다.

### 정답 비노출 입력팩

`arena-input-pack-v1`은 판단을 생성하는 대상에게 전달하기 위한 별도 파일입니다.

입력팩에는 다음만 포함합니다.

- 사례 식별자
- 사례 제목과 설명
- 공개 실행 요청
- 입력팩을 만든 원본 시나리오의 식별자와 SHA-256

다음 정보는 입력팩에 포함하지 않습니다.

- `expected_decision`
- 실행 결과 기대값
- `tags`
- 평가 메모
- 임의 metadata
- 외부 context 참조
- 비공개 프롬프트
- 시스템 메시지
- 내부 로그 또는 trace

현재 v1은 의도적으로 **자기완결적인 공개 요청만** 허용합니다. 별도 context나 임의 metadata가 필요한 경우에는 v1에 억지로 넣지 않고 공개 범위를 다시 검토한 뒤 새 포맷을 설계합니다.

## 1. 입력팩 생성

```bash
sea-ops-arena-input-pack \
  --suite examples/scenarios/public_suite_v2.json \
  --output model-input.json
```

생성된 파일은 허용 필드만 새 객체에 다시 작성하는 방식으로 만들어집니다. 원본 JSON을 복사한 뒤 몇 개의 키를 삭제하는 방식이 아닙니다.

## 2. 판단 생성

모델·사람·외부 시스템에는 **`model-input.json`만 제공합니다.**

평가용 원본 시나리오의 `expected_decision`, 태그 또는 정답 파일은 판단 생성 과정에 제공하지 않습니다.

Arena 공개 저장소는 특정 모델 호출 코드나 비공개 시스템 연결 코드를 요구하지 않습니다. 호출은 별도 환경에서 수행하고 공개 가능한 최종 판단만 다음 단계로 가져옵니다.

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

이 템플릿에는 다음 두 해시가 함께 기록됩니다.

- `suite_sha256`: 평가에 사용될 정확한 시나리오 파일
- `input_pack_sha256`: 판단 생성 대상이 실제로 본 정답 비노출 입력팩

이후 `decisions`의 `__FILL__` 값만 `proceed`, `reject`, `defer` 중 하나로 채웁니다.

원본 응답 전문, 프롬프트, 추론 과정, 로그 등을 템플릿에 복사하지 않습니다.

## 4. 평가

실제 외부 결과는 평가 시에도 입력팩을 함께 제공해야 합니다.

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --decisions model-run-001.public.json
```

Arena는 다음을 확인한 뒤 평가합니다.

1. 결과 파일의 `suite_sha256`이 평가용 시나리오와 일치하는가
2. 입력팩의 `source_suite.sha256`이 평가용 시나리오와 일치하는가
3. 결과 파일의 `input_pack_sha256`이 제공된 입력팩과 일치하는가
4. 모든 요청 ID의 결과가 빠짐없이 존재하는가

하나라도 일치하지 않으면 평가를 거부합니다.

## 5. 비교와 반복 평가

실제 외부 결과를 비교할 때도 동일한 입력팩을 명시합니다.

```bash
sea-ops-arena-compare \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --decisions model-a.public.json model-b.public.json
```

반복 평가 역시 동일합니다.

```bash
sea-ops-arena-repeat \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --results run-001.public.json run-002.public.json run-003.public.json
```

## 6. 공개 전 감사

실제 외부 결과를 저장소에 공개하려면 해당 결과가 참조하는 정답 비노출 입력팩도 함께 공개하는 것을 기본으로 합니다.

```bash
sea-ops-arena-audit --root .
```

공개 감사는 실제 결과에 필요한 해시가 있는지, 참조된 입력팩이 저장소에 존재하는지, 공개 결과·입력팩 포맷이 유효한지 확인합니다.

자동 감사만으로 비공개 기술의 의미적 유출 여부를 판단할 수는 없습니다. 내부 명칭 검사와 여러 공개 파일을 조합했을 때의 역추론 가능성 검토는 별도의 공개 전 검토로 유지합니다.

## 왜 이렇게 분리하나

정답을 공개하는 것은 벤치마크의 계산 방법을 투명하게 만드는 데 유리합니다. 그러나 같은 파일을 판단 생성 대상에게 전달하면 평가 자체가 무의미해질 수 있습니다.

따라서 SEA Ops Arena는 **평가 기준의 공개 가능성**과 **실제 판단 생성 시의 정답 비노출**을 파일 수준에서 분리합니다.

이 분리는 SEA 또는 다른 연결 시스템의 내부 구현을 공개하기 위한 장치가 아닙니다. 외부에서 확인해야 할 것은 어떤 입력이 주어졌고 어떤 최종 판단이 나왔으며 어떻게 평가되었는지까지입니다.
