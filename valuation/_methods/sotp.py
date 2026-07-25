"""SOTP(Sum-of-the-Parts): 이질적인 사업부문을 각각 배수로 평가한 뒤 합산.

세그먼트마다 성장률·마진·적정배수가 크게 다른 회사(예: 삼성에스디에스의
IT서비스/클라우드/물류BPO)에 적합. 배수를 단일 연결 실적에 뭉뚱그려 적용하면
고성장 사업부가 저성장 사업부에 의해 가려지는 왜곡이 생기는 걸 피하기 위함.
"""
from .errors import MissingInputError
from ._common import require


def calculate(a: dict) -> dict:
    missing = []

    segments = a.get("segments", {})
    seg_values = {}
    for name, node in segments.items():
        metric = require(node.get("metric"), f"sotp.segments.{name}.metric", missing)
        multiple = require(node.get("multiple"), f"sotp.segments.{name}.multiple", missing)
        if metric is not None and multiple is not None:
            seg_values[name] = metric * multiple

    net_debt = require(a.get("net_debt"), "sotp.net_debt", missing)
    shares = require(a.get("shares_outstanding"), "sotp.shares_outstanding", missing)

    if missing:
        raise MissingInputError(missing)

    enterprise_value = sum(seg_values.values())
    equity_value = enterprise_value - net_debt
    return {
        "segment_values": seg_values,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "value_per_share": equity_value / shares,
    }
