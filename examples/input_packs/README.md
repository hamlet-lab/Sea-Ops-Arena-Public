# 공식 Baseline 입력팩

이 디렉터리는 실제 외부 baseline 실험에 사용하는 **고정(frozen) 공개 입력팩**을 보관합니다.

## 현재 공식 입력팩

- 파일: `public_suite_v2.input.json`
- 스키마: `arena-input-pack-v2`
- 원본 평가 세트: `../scenarios/public_suite_v2.json`
- SHA-256: `e68cf82311d4c4b6477799cf61aeb28b4f446d997e5a3c82b3c6ebb9680b88db`

해시는 `public_suite_v2.input.sha256`에도 기록되어 있습니다.

이 입력팩에는 공개 과제 정의, 세 가지 최종 상태의 의미, 실행 제약, 12개 합성 사례가 포함됩니다. 평가 기대값과 평가 태그는 포함하지 않습니다.

## 변경 규칙

실제 baseline 결과가 이 입력팩의 SHA-256을 참조하기 시작한 뒤에는 같은 파일을 수정하지 않습니다.

과제 정의, 실행 제약, 사례 또는 직렬화 결과가 달라져 SHA-256이 바뀌어야 한다면 기존 파일을 덮어쓰지 않고 **새 입력팩 버전**을 만듭니다. 서로 다른 해시의 결과는 동일 실험으로 묶지 않습니다.

## 재생성 확인

```bash
sea-ops-arena-input-pack \
  --suite examples/scenarios/public_suite_v2.json \
  --output /tmp/public_suite_v2.input.json

cmp /tmp/public_suite_v2.input.json examples/input_packs/public_suite_v2.input.json
```

해시 확인:

```bash
cd examples/input_packs
sha256sum -c public_suite_v2.input.sha256
```

GitHub Actions에서도 두 검사를 수행합니다.

이 디렉터리는 공개 benchmark 입력만 다룹니다. 비공개 시스템의 내부 구현, 정책, 상태, 판단 과정 또는 원본 실행 로그를 저장하지 않습니다.
