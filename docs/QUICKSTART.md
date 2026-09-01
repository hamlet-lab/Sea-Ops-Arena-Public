# 빠른 실행

이 저장소의 기본 데모는 외부 API 키나 실제 운영 시스템 없이 실행할 수 있습니다.

## 설치

Python 3.11 이상을 권장합니다.

```bash
python -m pip install -e .
```

## 1. 기본 합성 데모

```bash
python -m sea_ops_arena.demo
```

기본값은 `balanced` 프로필이며 Markdown 형식의 결과를 출력합니다.

## 2. 서로 다른 공개 예시 응답 비교

```bash
python -m sea_ops_arena.demo --profile eager
python -m sea_ops_arena.demo --profile cautious
```

세 프로필은 실제 모델이 아니라 Arena의 집계 차이를 확인하기 위한 고정된 예시입니다.

- `balanced`: 공개 기대값과 동일하게 준비된 응답
- `eager`: 모든 요청을 진행하는 예시 응답
- `cautious`: 모든 요청을 보류하는 예시 응답

## 3. JSON 결과 출력

```bash
python -m sea_ops_arena.demo --profile balanced --format json
```

JSON 출력은 자동 집계나 외부 시각화 도구와 연결할 때 사용할 수 있습니다.

## 4. 외부 JSON 파일로 벤치마크 실행

공개 시나리오와 공개 판단 결과를 파일로 분리해 같은 Arena에서 실행할 수 있습니다.

```bash
sea-ops-arena \
  --suite examples/scenarios/public_demo_v1.json \
  --decisions examples/decisions/balanced.json
```

JSON 보고서가 필요하면 다음과 같이 실행합니다.

```bash
sea-ops-arena \
  --suite examples/scenarios/public_demo_v1.json \
  --decisions examples/decisions/eager.json \
  --format json
```

이 구조를 사용하면 Arena 코드를 바꾸지 않고 새로운 공개 시나리오나 외부 시스템의 공개 판단 결과를 입력할 수 있습니다.

## 5. 예제 파일

- `examples/scenarios/public_demo_v1.json`: 세 개의 합성 운영 사례
- `examples/decisions/balanced.json`: 공개 기대값과 일치하는 고정 예시
- `examples/decisions/eager.json`: 모든 요청을 진행하는 고정 예시
- `examples/decisions/cautious.json`: 모든 요청을 보류하는 고정 예시
- `examples/DEMO_RESULTS.md`: 세 응답 패턴의 결과 비교 예시

## 6. 테스트

```bash
python -m pytest
```

테스트는 공개 하네스와 공개 지표의 동작만 검증합니다. 비공개 의사결정 시스템의 내부 규칙이나 구조를 검증하지 않습니다.

GitHub Actions에서도 같은 공개 테스트를 자동 실행합니다.

## 결과를 볼 때 주의할 점

현재 기본 데모는 **합성 시나리오 + 고정 응답**으로 이루어져 있습니다. 따라서 여기서 나오는 수치를 실제 SEA 성능, 실제 AI 모델 성능, 산업 현장 성능으로 해석하면 안 됩니다.

실제 비교 결과가 추가될 경우에는 모델명, 실행 조건, 시나리오 버전, 결과 원문과 함께 별도로 표시합니다.
