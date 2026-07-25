# valuation/

종목별 밸류에이션을 기법(method)별로 분리해 계산하는 프레임워크.

## 구조

```
valuation/
  _methods/            기법별 계산 모듈 (assumptions.yaml -> 결과 dict)
    dcf.py              현금흐름할인
    nav.py              지주회사 순자산가치(지분가치 합산 + 할인)
    sotp.py             사업부문별 합산가치
    normalized_per.py   일회성 항목 제거 후 PER 적용
    errors.py           MissingInputError
    _common.py          공통 헬퍼
  run_valuation.py     실행 스크립트
  <종목명>/
    config.yaml         이 종목에 적용할 기법(보통 2개)과 선택 근거, 제외한 기법과 이유
    assumptions.yaml    기법별 입력값. 모든 숫자는 source를 명시하거나 확인 불가로 남김
```

## 핵심 원칙

**출처 없는 숫자로는 계산하지 않는다.** `assumptions.yaml`의 각 값은
`{value: ..., source: "..."}` 형태이고, `value`가 `null`이면 해당 계산은
`MissingInputError`로 거부된다. 실행 결과는 계산된 숫자 대신
"계산 불가 — 다음 입력이 없습니다: [...]" 를 보여준다. 이는 버그가 아니라
설계 의도다 — 출처 없는 값을 추정치로 채워서 사실처럼 보여주지 않기 위함.

## 실행 방법

```bash
cd valuation
python3 run_valuation.py 휴젤
python3 run_valuation.py 삼성에피스홀딩스
python3 run_valuation.py 삼성에스디에스
python3 run_valuation.py --all
```

## assumptions.yaml 값 채우는 규칙

```yaml
필드명:
  value: 123.4          # 숫자 없으면 null
  unit: "KRW"            # 선택
  source: "출처 텍스트"   # value가 null이면 "확인 불가"라고 적을 것
```

시나리오별(강세/기본/약세)로 나뉘는 값(성장률, 배수, 할인율 등)은 아래처럼:

```yaml
growth_rate:
  bull: { value: 0.15, source: "..." }
  base: { value: 0.08, source: "..." }
  bear: { value: 0.02, source: "..." }
```

## 새 종목 추가하기

1. `mkdir valuation/<종목명>`
2. `config.yaml` 작성 — 적용할 기법 2개(원칙)와 그 선택 근거, 제외한 기법과 이유
3. `assumptions.yaml` 작성 — 확보한 값은 출처와 함께, 못 찾은 값은 `value: null` +
   `source: "확인 불가"`로
4. `python3 run_valuation.py <종목명>`으로 실행해 어떤 입력이 더 필요한지 확인

## 현재 상태 (2026-07-25 기준)

세 종목(휴젤, 삼성에피스홀딩스, 삼성에스디에스) 모두 뉴스 검색 기반 조사만으로는
DCF/NAV/SOTP/정상화PER을 끝까지 계산할 만큼의 1차 자료(DART 공시, 재무제표 원문,
peer 배수 비교)를 확보하지 못한 상태. `run_valuation.py --all` 실행 결과에 나오는
"계산 불가" 목록이 곧 다음에 채워야 할 자료 목록이다.
