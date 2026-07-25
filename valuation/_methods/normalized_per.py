"""정상화 PER: 일회성 항목을 제거한 순이익에 배수를 곱해 적정가치를 추정.

일회성 비용/이익(소송 충당금, 퇴직급여 기준 변경, 자산 처분손익 등)이 섞인
보고 순이익을 그대로 배수화하면 왜곡되는 경우에 사용.

EPS는 두 가지 방식으로 구할 수 있다:
  (a) reported_net_income + shares_outstanding (+ one_off_items)로 계산 - 회사
      단위 실적을 직접 정상화할 때
  (b) 시나리오별 per_multiple[scenario]에 eps를 직접 지정 - 애널리스트마다 EPS
      추정치 자체가 다를 때(예: 12MF EPS vs 2027~2028 평균 EPS). 이 경우 (a)의
      공통 normalized_eps 대신 그 시나리오만의 eps를 쓴다.
"""
from .errors import MissingInputError
from ._common import require


def _common_eps(a: dict):
    """공통 정상화 EPS를 계산. 필요한 값이 없으면 (None, missing_fields)를 반환."""
    missing = []
    reported_income = require(a.get("reported_net_income"), "normalized_per.reported_net_income", missing)
    shares = require(a.get("shares_outstanding"), "normalized_per.shares_outstanding", missing)

    one_off_total = 0.0
    for i, item in enumerate(a.get("one_off_items", []) or []):
        v = require(item.get("amount"), f"normalized_per.one_off_items[{i}].amount", missing)
        if v is not None:
            one_off_total += v

    if missing:
        return None, missing, None, None

    normalized_income = reported_income - one_off_total
    return normalized_income / shares, [], reported_income, one_off_total


def calculate(a: dict) -> dict:
    common_eps, common_missing, reported_income, one_off_total = _common_eps(a)

    result = {"scenarios": {}}
    if common_eps is not None:
        result["reported_net_income"] = reported_income
        result["one_off_total"] = one_off_total
        result["normalized_eps"] = common_eps

    multiple = a.get("per_multiple", {})
    scenario_missing = {}

    for scenario in ("bull", "base", "bear"):
        node = multiple.get(scenario)
        if node is None:
            continue

        if "eps" in node and "multiple" in node:
            # 이 시나리오만의 EPS를 직접 지정한 경우 (애널리스트별 EPS 추정 차이 반영)
            miss = []
            eps = require(node.get("eps"), f"normalized_per.per_multiple.{scenario}.eps", miss)
            m = require(node.get("multiple"), f"normalized_per.per_multiple.{scenario}.multiple", miss)
            if miss:
                scenario_missing[scenario] = miss
                continue
            result["scenarios"][scenario] = {
                "eps": eps,
                "per_multiple": m,
                "value_per_share": eps * m,
                "eps_source": "시나리오 전용 EPS (공통 normalized_eps 아님)",
            }
        else:
            # 공통 normalized_eps에 배수만 다르게 적용하는 경우
            if common_eps is None:
                scenario_missing[scenario] = common_missing
                continue
            miss = []
            m = require(node, f"normalized_per.per_multiple.{scenario}", miss)
            if miss:
                scenario_missing[scenario] = miss
                continue
            result["scenarios"][scenario] = {
                "per_multiple": m,
                "value_per_share": common_eps * m,
            }

    if not result["scenarios"]:
        # 아무 시나리오도 계산 못 했으면 명확히 실패 처리 (중복 제거, 순서 유지)
        seen = []
        for miss in [common_missing, *scenario_missing.values()]:
            for field in miss:
                if field not in seen:
                    seen.append(field)
        raise MissingInputError(seen or ["normalized_per.per_multiple"])

    if scenario_missing:
        result["scenario_missing"] = scenario_missing
    return result
