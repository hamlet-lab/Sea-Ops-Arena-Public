# SEA Ops Arena

SEA Ops Arena는 **AI가 실제 운영 환경에 영향을 주는 행동을 제안할 때, 그 결과를 안전하고 재현 가능한 방식으로 검증하기 위한 공개 벤치마크·평가 환경**입니다.

이 저장소에는 SEA의 내부 구현체가 아니라, 외부에서 확인하고 반복 실행할 수 있는 **Arena(검증 환경)**만 공개합니다.

외부 심사·검토 목적으로 처음 방문했다면 [`docs/REVIEWER_GUIDE.md`](docs/REVIEWER_GUIDE.md)의 **3분 가이드**부터 보는 것을 권장합니다.

> 현재 저장소에 포함된 기본 결과는 합성 시나리오와 고정 응답입니다. **실제 AI 모델 또는 SEA 성능 결과가 아닙니다.**

## 현재 공개판 — v0.6

현재 공개판은 4개 운영 영역의 **12개 합성 시나리오**를 실행·비교·반복 평가할 수 있으며, 실제 외부 결과를 만들 때 평가 정답이 입력에 섞이지 않도록 별도의 **정답 비노출 입력팩**을 생성합니다.

`arena-input-pack-v2`에는 사례뿐 아니라 공개 과제 정의와 baseline 실행 제약까지 함께 들어가므로, 파일의 SHA-256 하나로 **모델이 본 문제와 지시 조건 전체**를 고정할 수 있습니다.

- JSON 기반 공개 시나리오 실행
- 정답·평가 태그가 제거된 `arena-input-pack-v2` 생성
- 입력팩 안에 공개 과제 정의와 `proceed / reject / defer` 의미 고정
- 첫 baseline에서 외부 검색·도구 사용 금지 조건 고정
- JSON 기반 공개 판단 결과 입력
- 여러 결과의 동일 조건 비교
- 반복 실행의 판단 안정성 집계
- 판단 일치율 / 불필요 실행 / 필요한 실행 누락 / 실행 성공률 집계
- Markdown / JSON 결과 보고서
- 입력 파일 SHA-256 기반 재현 식별자
- `manifest.json` + `report.md` + `results.json` 결과 묶음
- 실제 외부 결과의 `suite_sha256` 결합 검증
- 실제 외부 결과의 `input_pack_sha256` 결합 검증
- 허용 필드만 받는 `public-decision-set-v1`
- 원본 로그를 복사하지 않는 공개 결과 템플릿 생성
- 일반적인 공개 위험을 검사하는 릴리스 감사
- GitHub Actions 기반 테스트와 CLI 재현 경로 검증

## 공개 구조

```text
평가용 공개 시나리오
        |
        |  정답·평가 메타데이터 제거
        v
정답 비노출 입력팩 v2  ---->  AI 모델 / 사람 / 외부 시스템
  + 공개 과제 정의                |
  + 실행 제약                     v
                              최종 판단 결과
                                   |
                                   v
                          공개 결과 최소 포맷
                                   |
                                   v
평가용 공개 시나리오  ------>  Arena 평가 / 비교 / 반복성
```

연결된 시스템이 내부에서 어떤 방식으로 판단하는지는 Arena가 알 필요가 없습니다.

## 12개 공개 시나리오

대표 공개 세트는 다음 네 영역으로 구성됩니다.

| 영역 | 사례 수 | 예시 |
|---|---:|---|
| 고객지원 | 3 | 정상 요청, 입력 충돌, 정보 누락 |
| 사무 운영 | 3 | 정상 구매, 정보 누락, 중복 요청 |
| 재고 관리 | 3 | 정상 보충, 중복 작업, 수량 충돌 |
| 시설 운영 | 3 | 정기 점검, 대상 불일치, 경보 점검 |

모든 사례는 공개용으로 새로 만든 합성 문제이며, 비공개 시스템의 정책이나 내부 규칙을 복제하지 않습니다. 자세한 작성 원칙은 [`docs/SCENARIOS.md`](docs/SCENARIOS.md)에 있습니다.

## 빠르게 실행해 보기

Python 3.11 이상 환경에서 설치합니다.

```bash
python -m pip install -e .
```

합성 fixture를 사용한 기본 실행:

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions examples/decisions/v2-balanced.json
```

여러 합성 결과를 한 번에 비교:

```bash
sea-ops-arena-compare \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions \
    examples/decisions/v2-balanced.json \
    examples/decisions/v2-eager.json \
    examples/decisions/v2-cautious.json
```

반복 결과의 안정성 확인:

```bash
sea-ops-arena-repeat \
  --suite examples/scenarios/public_suite_v2.json \
  --results \
    examples/results/v2-balanced.public.json \
    examples/results/v2-repeat-002.public.json \
    examples/results/v2-repeat-003.public.json
```

위 결과들은 실제 모델이 아니라 Arena 기능을 보여 주기 위한 fixture입니다.

## 실제 외부 결과를 평가할 때

실제 모델·사람·외부 시스템에는 `public_suite_v2.json`을 그대로 입력하지 않습니다. 이 파일에는 외부에서 평가 계산을 재현하기 위한 기대 판단과 평가용 정보가 포함되어 있기 때문입니다.

### 1. 정답 비노출 입력팩 생성

```bash
sea-ops-arena-input-pack \
  --suite examples/scenarios/public_suite_v2.json \
  --output model-input.json
```

`arena-input-pack-v2`에는 다음이 들어갑니다.

- 사례 설명과 공개 요청
- 공개 과제 정의
- `proceed` / `reject` / `defer`의 공개 의미
- 필요한 request ID 목록과 출력 계약
- `use_only_input_pack_content`
- `no_external_tools_or_retrieval`
- `return_final_status_map_only`

반대로 다음 평가 전용 정보는 포함하지 않습니다.

- `expected_decision`
- 실행 결과 기대값
- 평가 태그
- 평가 메모
- 임의 metadata
- 외부 context 참조

실제 판단 생성 대상에는 **이 입력팩만 제공합니다.**

### 2. 판단 생성은 별도 환경에서 수행

모델 호출 또는 비공개 시스템 실행 코드는 이 공개 저장소가 요구하지 않습니다.

첫 baseline은 같은 입력팩을 사용하고, 외부 검색·RAG·도구 없이, 이전 반복의 대화 상태를 재사용하지 않는 새 실행으로 최소 3회 수행하는 것을 기본 프로토콜로 합니다.

별도 환경에서 판단을 생성한 뒤 공개 가능한 최종 `proceed` / `reject` / `defer` 값만 다음 단계로 가져옵니다.

자세한 조건은 [`docs/BASELINE_PROTOCOL.md`](docs/BASELINE_PROTOCOL.md)에 있습니다.

### 3. 안전한 공개 결과 템플릿 생성

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

템플릿에는 두 개의 결합 해시가 기록됩니다.

- `suite_sha256` — 평가에 사용되는 정확한 시나리오 파일
- `input_pack_sha256` — 판단 생성 대상이 실제로 본 정답 비노출 입력팩 전체

입력팩 해시에는 사례와 공개 과제 정의, baseline 실행 제약이 모두 포함됩니다.

생성된 `__FILL__` 값만 최종 판단으로 채웁니다. 원본 프롬프트, 시스템 메시지, 응답 전문, 추론 과정, 내부 로그를 복사하지 않습니다.

### 4. 평가 시 입력팩까지 다시 검증

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --input-pack model-input.json \
  --decisions model-run-001.public.json
```

Arena는 평가 전에 다음을 확인합니다.

1. 결과의 `suite_sha256`이 현재 시나리오와 같은가
2. 입력팩이 그 시나리오에서 생성됐는가
3. 입력팩의 공개 과제와 실행 제약이 표준 계약과 일치하는가
4. 결과의 `input_pack_sha256`이 제공된 입력팩과 같은가
5. 모든 요청 ID의 결과가 빠짐없이 존재하는가

하나라도 맞지 않으면 평가하지 않습니다.

전체 절차는 [`docs/BLIND_EVALUATION.md`](docs/BLIND_EVALUATION.md)에 정리되어 있습니다.

## 공개 평가 지표

현재 공개판은 임의의 가중 종합점수나 순위를 만들지 않고 관찰값을 각각 보여 줍니다.

| 지표 | 의미 |
|---|---|
| 판단 일치율 | 공개 시나리오의 기대 판단과 최종 결과가 일치한 비율 |
| 불필요 실행 | 실행하지 않아야 하는 사례에서 실행이 진행된 횟수 |
| 필요한 실행 누락 | 실행해야 하는 사례에서 실행되지 않은 횟수 |
| 실행 성공률 | 실제 시도된 실행 가운데 합성 환경의 공개 기대 결과와 일치한 비율 |
| 반복 판단 안정률 | 동일 조건의 여러 공개 결과에서 최종 판단이 계속 동일한 사례의 비율 |

평가 지표의 자세한 의미는 [`docs/EVALUATION.md`](docs/EVALUATION.md)를 참고해 주세요.

## 재현 가능한 결과 묶음

```bash
sea-ops-arena \
  --suite examples/scenarios/public_suite_v2.json \
  --decisions examples/decisions/v2-balanced.json \
  --output-dir runs
```

`runs/<run_id>/` 아래에 다음이 생성됩니다.

- `manifest.json` — 공개 입력 파일 해시와 요약 지표
- `report.md` — 사람이 읽는 한국어 결과
- `results.json` — 후속 분석용 구조화 결과

manifest에는 호스트명, 환경변수, 내부 경로 또는 비공개 판단 과정이 기록되지 않습니다.

## 공개 릴리스 감사

```bash
sea-ops-arena-audit --root .
```

자동 감사는 다음과 같은 일반적인 위험을 검사합니다.

- `.env`
- 키·인증서 형식 파일
- 공개 저장소에서 사용하지 않는 위험 경로
- 엄격 공개 결과 포맷 오류
- 정답 비노출 입력팩 포맷과 공개 과제 계약 오류
- 실제 결과가 참조하는 시나리오 해시
- 실제 결과가 참조하는 입력팩 해시와 입력팩 파일의 존재

**내부 비밀명 deny-list는 이 공개 저장소에 넣지 않습니다.** 내부 명칭과 여러 공개 파일을 조합했을 때의 역추론 위험은 저장소 밖에서 별도로 검토합니다. 자동 감사의 범위와 한계는 [`docs/PUBLIC_AUDIT.md`](docs/PUBLIC_AUDIT.md)를 참고해 주세요.

## 무엇을 공개하나

- 합성 공개 시나리오
- 정답 비노출 모델 입력 형식과 공개 benchmark 과제
- 공개 가능한 최종 판단 결과 형식
- 공개 시뮬레이터 결과
- 일반적인 점수화·비교·반복성·보고서·재현 도구
- 외부 시스템과 연결되는 최소 인터페이스

## 무엇을 공개하지 않나

- SEA 내부 구현 코드
- 내부 상태 표현 방식
- 비공개 정책·판단·권한 처리 로직
- 내부 검증 및 실행 제어 구조
- 비공개 아키텍처 문서
- 연구·특허 관련 비공개 자료
- 실제 운영 환경의 연결 정보
- 원본 비공개 프롬프트·시스템 메시지
- 내부 추론·작업 로그·trace

공개 범위는 **외부에서 독립적으로 확인해야 하는 입력·최종 결과·평가·재현 표면까지**입니다.

세부 공개 원칙은 [`docs/PUBLIC_BOUNDARY.md`](docs/PUBLIC_BOUNDARY.md)에 있습니다.

## 문서

- [`docs/REVIEWER_GUIDE.md`](docs/REVIEWER_GUIDE.md) — 외부 검토자용 3분 가이드
- [`docs/QUICKSTART.md`](docs/QUICKSTART.md) — 실행 방법
- [`docs/BLIND_EVALUATION.md`](docs/BLIND_EVALUATION.md) — 정답 비노출 실제 평가 절차
- [`docs/BASELINE_PROTOCOL.md`](docs/BASELINE_PROTOCOL.md) — 첫 실제 모델 baseline 조건
- [`docs/PUBLIC_RESULTS.md`](docs/PUBLIC_RESULTS.md) — 공개 결과 파일 규칙
- [`docs/EVALUATION.md`](docs/EVALUATION.md) — 평가 지표
- [`docs/SCENARIOS.md`](docs/SCENARIOS.md) — 합성 시나리오 작성 원칙
- [`docs/PUBLIC_AUDIT.md`](docs/PUBLIC_AUDIT.md) — 자동 공개 감사 범위
- [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md) — 공개 전 체크리스트
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — 공개판 개발 로드맵

## 저장소 운영 원칙

이 저장소는 공개 전용 코드베이스이며 비공개 개발 저장소의 Git 이력을 상속하지 않습니다. 공개할 수 있는 내용만 별도로 작성하고 관리합니다.

## 보안 및 민감정보 제보

비공개 기술이나 민감정보가 실수로 포함되었다고 판단되는 경우 공개 Issue, Pull Request, Discussion에 내용을 그대로 게시하지 말아 주세요. 자세한 안내는 [`SECURITY.md`](SECURITY.md)를 참고해 주세요.
