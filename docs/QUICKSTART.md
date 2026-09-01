# 빠른 실행

이 저장소의 공개 예시는 외부 API 키나 실제 운영 시스템 없이 실행할 수 있습니다.

## 설치

Python 3.11 이상을 권장합니다.

```bash
python -m pip install -e .
```

## 1. 합성 fixture로 Arena 확인

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions examples/decisions/v2-balanced.json
```

`v2-balanced`는 공개 기대값과 동일하게 준비한 고정 예시이며 실제 모델 또는 SEA 성능이 아닙니다.

## 2. 여러 합성 결과 비교

```bash
sea-ops-arena-compare \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions \
    examples/decisions/v2-balanced.json \
    examples/decisions/v2-eager.json \
    examples/decisions/v2-cautious.json
```

비교 도구는 임의의 종합 순위를 만들지 않고 판단 일치율, 불필요 실행, 필요한 실행 누락, 실행 성공률을 나란히 보여 줍니다.

## 3. 반복 fixture의 안정성 확인

```bash
sea-ops-arena-repeat \
  --suite examples/scenarios/public_suite_v2.json \
  --results \
    examples/results/v2-balanced.public.json \
    examples/results/v2-repeat-002.public.json \
    examples/results/v2-repeat-003.public.json
```

이 예제들은 반복 집계 기능을 확인하기 위한 합성 fixture입니다.

---

# 실제 외부 결과를 만들 때

실제 모델·사람·외부 시스템 결과를 만들 때는 평가용 시나리오 파일을 그대로 판단 생성 대상에 전달하지 않습니다.

## 4. 정답 비노출 입력팩 생성

```bash
sea-ops-arena-input-pack \
  --suite examples/scenarios/public_suite_v2.json \
  --output model-input.json
```

입력팩에는 공개 요청이 남고 다음 평가 전용 정보는 제거됩니다.

- 기대 판단
- 평가 태그
- 평가 메모
- 실행 결과 기대값
- 임의 metadata
- 외부 context 참조

판단 생성 대상에는 **`model-input.json`만** 제공합니다.

## 5. 별도 환경에서 판단 생성

모델 호출 또는 비공개 시스템 실행은 별도 환경에서 수행합니다.

Arena 공개 저장소에 원본 프롬프트, 시스템 메시지, 응답 전문, 내부 로그를 가져오지 않습니다.

공개 단계로 가져올 것은 각 request ID에 대응하는 최종 `proceed`, `reject`, `defer`뿐입니다.

## 6. 안전한 공개 결과 템플릿 생성

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

템플릿은 다음을 자동 기록합니다.

- 평가용 시나리오의 `suite_sha256`
- 모델이 본 입력팩의 `input_pack_sha256`
- 모든 request ID
- 공개 가능한 최소 출처 정보

`decisions`의 `__FILL__` 값만 최종 판단으로 채웁니다.

## 7. 실제 결과 평가

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --decisions model-run-001.public.json
```

실제 외부 결과는 `--input-pack`이 없거나 해시가 맞지 않으면 평가되지 않습니다.

## 8. 실제 결과 비교

```bash
sea-ops-arena-compare \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --decisions model-a.public.json model-b.public.json
```

두 결과가 같은 정답 비노출 입력에서 생성됐는지 각 파일의 해시 결합을 검증한 뒤 비교합니다.

## 9. 실제 반복 결과 평가

```bash
sea-ops-arena-repeat \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --results run-001.public.json run-002.public.json run-003.public.json
```

반복 판단 안정률은 공개된 최종 판단이 반복 간 동일한지만 측정합니다.

## 10. 재현 가능한 결과 묶음

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions examples/decisions/v2-balanced.json \
  --output-dir runs
```

`runs/<run_id>/` 아래에 다음이 생성됩니다.

- `manifest.json`
- `report.md`
- `results.json`

합성 fixture 경로에서는 간단한 입력 두 파일로 재현 식별자를 생성합니다. 실제 외부 결과의 입력팩 결합 정보는 엄격 공개 결과 파일 자체에서 별도로 검증됩니다.

## 11. 공개 릴리스 감사

```bash
sea-ops-arena-audit --root .
```

감사 도구는 일반적인 위험 파일, 엄격 공개 결과 포맷, 정답 비노출 입력팩 포맷, 실제 결과가 참조하는 시나리오와 입력팩 해시를 확인합니다.

실제 외부 결과가 저장소에 있다면 그 결과가 참조하는 입력팩 파일도 저장소에 존재해야 합니다.

## 12. 테스트

```bash
python -m pytest
```

GitHub Actions에서는 테스트뿐 아니라 입력팩 생성, 단일 평가, 비교, 반복 평가, 공개 결과 템플릿 생성 경로를 함께 확인합니다.

## 더 자세히 보기

- [`BLIND_EVALUATION.md`](BLIND_EVALUATION.md) — 정답 비노출 평가 절차
- [`PUBLIC_RESULTS.md`](PUBLIC_RESULTS.md) — 결과 파일 규칙
- [`EVALUATION.md`](EVALUATION.md) — 평가 지표
- [`PUBLIC_AUDIT.md`](PUBLIC_AUDIT.md) — 자동 감사의 범위와 한계
