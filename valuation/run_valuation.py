#!/usr/bin/env python3
"""회사 폴더의 config.yaml + assumptions.yaml을 읽어 지정된 기법으로 계산한다.

사용법:
    python3 run_valuation.py <회사폴더명>          # 예: python3 run_valuation.py 휴젤
    python3 run_valuation.py --all                # 전체 회사 폴더 순회
"""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from _methods import METHODS
from _methods.errors import MissingInputError

ROOT = Path(__file__).parent


def fmt(x):
    if isinstance(x, float):
        return f"{x:,.2f}"
    if isinstance(x, int):
        return f"{x:,}"
    return x


def print_result(result, indent=0):
    pad = "  " * indent
    for k, v in result.items():
        if k == "yearly":
            continue
        if isinstance(v, dict):
            print(f"{pad}{k}:")
            print_result(v, indent + 1)
        else:
            print(f"{pad}{k}: {fmt(v)}")


def run_company(company: str):
    base = ROOT / company
    if not base.is_dir():
        print(f"[{company}] 폴더 없음: {base}")
        return

    config = yaml.safe_load((base / "config.yaml").read_text(encoding="utf-8"))
    assumptions = yaml.safe_load((base / "assumptions.yaml").read_text(encoding="utf-8"))

    print(f"\n{'=' * 60}")
    print(f"{company} 밸류에이션 (기준일: {config.get('as_of', '?')})")
    print(f"{'=' * 60}")

    for method_name in config.get("methods", []):
        rationale = (config.get("rationale") or {}).get(method_name, "")
        print(f"\n## {method_name}")
        if rationale:
            print(f"선택 근거: {rationale.strip()}")

        module = METHODS.get(method_name)
        if module is None:
            print(f"알 수 없는 기법: {method_name}")
            continue

        section = assumptions.get(method_name, {})
        try:
            result = module.calculate(section)
        except MissingInputError as e:
            print(f"계산 불가 — 다음 입력이 assumptions.yaml에 없습니다 (value: null):")
            for field in e.fields:
                print(f"  - {field}")
            continue
        except ValueError as e:
            print(f"계산 불가 — {e}")
            continue

        print_result(result, indent=1)

    excluded = config.get("excluded_methods")
    if excluded:
        print(f"\n## 적용하지 않은 기법과 이유")
        for name, reason in excluded.items():
            print(f"  - {name}: {reason}")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    arg = sys.argv[1]
    if arg == "--all":
        for path in sorted(ROOT.iterdir()):
            if path.is_dir() and not path.name.startswith("_"):
                run_company(path.name)
    else:
        run_company(arg)


if __name__ == "__main__":
    main()
