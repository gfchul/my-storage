def require(node, path, missing):
    """node는 {"value": ..., "source": "..."} 형태. value가 없으면 path를 missing에 기록하고 None 반환."""
    if node is None or node.get("value") is None:
        missing.append(path)
        return None
    return node["value"]


def optional(node, default=None):
    if node is None:
        return default
    return node.get("value", default)
