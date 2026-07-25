"""DCF: 잉여현금흐름을 시나리오별로 추정해 현재가치로 할인·합산."""
from .errors import MissingInputError
from ._common import require


def calculate(a: dict) -> dict:
    missing = []

    fcf_base = require(a.get("fcf_base"), "dcf.fcf_base", missing)
    discount_rate = require(a.get("discount_rate"), "dcf.discount_rate", missing)
    terminal_growth = require(a.get("terminal_growth_rate"), "dcf.terminal_growth_rate", missing)
    years = require(a.get("years"), "dcf.years", missing)
    shares = require(a.get("shares_outstanding"), "dcf.shares_outstanding", missing)
    net_debt = require(a.get("net_debt"), "dcf.net_debt", missing)

    if missing:
        raise MissingInputError(missing)

    if discount_rate <= terminal_growth:
        raise ValueError("discount_rate는 terminal_growth_rate보다 커야 함 (영구가치 발산)")

    growth = a.get("growth_rate", {})
    scenario_rates = {}
    growth_missing = []
    for scenario in ("bull", "base", "bear"):
        rate = require(growth.get(scenario), f"dcf.growth_rate.{scenario}", growth_missing)
        if rate is not None:
            scenario_rates[scenario] = rate

    result = {}
    if growth_missing:
        result["growth_rate_missing"] = growth_missing
    for scenario, rate in scenario_rates.items():
        fcf = fcf_base
        pv_sum = 0.0
        yearly = []
        for y in range(1, years + 1):
            fcf = fcf * (1 + rate)
            pv = fcf / ((1 + discount_rate) ** y)
            pv_sum += pv
            yearly.append({"year": y, "fcf": fcf, "pv": pv})

        terminal_fcf = fcf * (1 + terminal_growth)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth)
        terminal_pv = terminal_value / ((1 + discount_rate) ** years)

        enterprise_value = pv_sum + terminal_pv
        equity_value = enterprise_value - net_debt
        result[scenario] = {
            "growth_rate": rate,
            "enterprise_value": enterprise_value,
            "terminal_value_pv": terminal_pv,
            "equity_value": equity_value,
            "value_per_share": equity_value / shares,
            "yearly": yearly,
        }
    return result
