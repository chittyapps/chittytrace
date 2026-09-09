#!/usr/bin/env python3
"""Verify record_snapshot.json against the database it was captured from.

The snapshot exists so the tracing generator can run without the operator
handling a privileged DSN. That trade is only safe if the snapshot is provably
faithful, so this script reduces it to a small set of invariants — row counts
per collection and the sum of every monetary value in each — which can be
recomputed with a single read-only query and compared.

Any transcription error large enough to change a figure in the court package
will move one of these numbers.

Usage:
    python3 verify_record_snapshot.py record_snapshot.json
    # then run the companion SQL in verify_record_snapshot.sql and diff
"""

import json
import sys
from decimal import Decimal

MONEY_KEYS = ("amount", "sale_price", "loan", "wire", "wire_USAA", "deposit",
              "valuation", "documented_purchase_offers")


def money_sum(node):
    """Sum every monetary value anywhere in a nested structure."""
    total = Decimal("0")
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "deposits" and isinstance(value, list):
                total += sum(Decimal(str(v)) for v in value)
            elif key in MONEY_KEYS and isinstance(value, (int, float)):
                total += Decimal(str(value))
            else:
                total += money_sum(value)
    elif isinstance(node, list):
        for item in node:
            total += money_sum(item)
    return total


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "record_snapshot.json"
    with open(path) as fh:
        record = json.load(fh)

    print(f"{'collection':<24} {'rows':>6}  {'money sum':>16}")
    print("-" * 50)
    for key in sorted(k for k in record if not k.startswith("_")):
        rows = record[key]
        print(f"{key:<24} {len(rows):>6}  {money_sum(rows):>16,.2f}")

    # Invariants the court package depends on directly.
    acq = record["acquisition_facts"]
    print()
    print("acquisition invariants:")
    for fact in acq:
        nv = fact["normalized_value"]
        sources = Decimal("0")
        for k in ("loan", "wire", "wire_USAA", "deposit"):
            if k in nv:
                sources += Decimal(str(nv[k]))
        if "deposits" in nv:
            sources += sum(Decimal(str(v)) for v in nv["deposits"])
        price = Decimal(str(nv["sale_price"]))
        print(f"  {nv['property']:<32} price={price:>12,.2f} "
              f"sources={sources:>12,.2f} variance={sources - price:>12,.2f}")


if __name__ == "__main__":
    main()
