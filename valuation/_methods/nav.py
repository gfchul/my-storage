"""NAV: 지주회사가 보유한 지분가치 + 순현금을 합산한 뒤 지주사 할인을 적용.

지주회사(예: 삼성에피스홀딩스) 밸류에이션에 쓰는 방식. 자회사 지분가치는
개별적으로 출처가 있는 값이어야 하며(예: 공정가치 평가, 최근 거래가), 시가총액을
역산해서 다시 넣으면 순환참조가 되므로 사용하지 않는다.
"""
from .errors import MissingInputError
from ._common import require


def calculate(a: dict) -> dict:
    missing = []

    stakes = a.get("stakes", {})
    stake_total = 0.0
    for name, node in stakes.items():
        v = require(node, f"nav.stakes.{name}", missing)
        if v is not None:
            stake_total += v

    net_cash = require(a.get("net_cash"), "nav.net_cash", missing)
    shares = require(a.get("shares_outstanding"), "nav.shares_outstanding", missing)

    if missing:
        raise MissingInputError(missing)

    gross_nav = stake_total + net_cash
    nav_per_share = gross_nav / shares

    result = {
        "stake_total": stake_total,
        "net_cash": net_cash,
        "gross_nav": gross_nav,
        "nav_per_share": nav_per_share,
        "scenarios": {},
    }

    discount = a.get("holdco_discount", {})
    discount_missing = []
    for scenario in ("bull", "base", "bear"):
        node = discount.get(scenario)
        d = require(node, f"nav.holdco_discount.{scenario}", discount_missing)
        if d is not None:
            result["scenarios"][scenario] = {
                "holdco_discount": d,
                "value_per_share": nav_per_share * (1 - d),
            }
    if discount_missing:
        result["discount_missing"] = discount_missing
    return result
