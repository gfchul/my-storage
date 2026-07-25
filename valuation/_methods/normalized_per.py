"""정상화 PER: 일회성 항목을 제거한 순이익에 배수를 곱해 적정가치를 추정.

일회성 비용/이익(소송 충당금, 퇴직급여 기준 변경, 자산 처분손익 등)이 섞인
보고 순이익을 그대로 배수화하면 왜곡되는 경우에 사용.
"""
from .errors import MissingInputError
from ._common import require


def calculate(a: dict) -> dict:
    missing = []

    reported_income = require(a.get("reported_net_income"), "normalized_per.reported_net_income", missing)
    shares = require(a.get("shares_outstanding"), "normalized_per.shares_outstanding", missing)

    one_off_total = 0.0
    for i, item in enumerate(a.get("one_off_items", []) or []):
        v = require(item.get("amount"), f"normalized_per.one_off_items[{i}].amount", missing)
        if v is not None:
            one_off_total += v

    if missing:
        raise MissingInputError(missing)

    normalized_income = reported_income - one_off_total
    normalized_eps = normalized_income / shares

    result = {
        "reported_net_income": reported_income,
        "one_off_total": one_off_total,
        "normalized_net_income": normalized_income,
        "normalized_eps": normalized_eps,
        "scenarios": {},
    }

    multiple = a.get("per_multiple", {})
    multiple_missing = []
    for scenario in ("bull", "base", "bear"):
        m = require(multiple.get(scenario), f"normalized_per.per_multiple.{scenario}", multiple_missing)
        if m is not None:
            result["scenarios"][scenario] = {
                "per_multiple": m,
                "value_per_share": normalized_eps * m,
            }
    if multiple_missing:
        result["multiple_missing"] = multiple_missing
    return result
