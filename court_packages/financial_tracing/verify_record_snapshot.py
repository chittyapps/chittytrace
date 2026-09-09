#!/usr/bin/env python3
"""Recompute row counts and money sums from record_snapshot.json.

The snapshot exists so the tracing generator can run without the operator
handling a privileged DSN. That trade is only safe if the snapshot is provably
faithful, so this script reduces it to a small set of invariants — row counts
per collection and the sum of every monetary value in each.

This script reads only the local snapshot. It does not connect to the database
and cannot by itself prove anything. The proof is the comparison: run
`verify_record_snapshot.sql` against ChittyOS-Core and diff its output against
what this prints. Any transcription error large enough to change a figure in the
court package will move one of these numbers.

Usage:
    python3 verify_record_snapshot.py [record_snapshot.json]
"""

import json
import os
import sys
from decimal import Decimal

# The funding-source keys are defined once, by the generator. Importing them
# rather than restating them keeps the verifier's coverage identical to what the
# generator actually totals — a duplicated list would silently stop covering any
# key added on one side only, and a transcription error in that key would then
# pass verification.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from financial_tracing_court_package import SOURCE_KEYS  # noqa: E402

# Every key whose value is money, for the recursive collection totals. The
# funding-source keys come from the generator; the rest name amounts that appear
# only outside acquisition facts.
MONEY_KEYS = tuple(k for k in SOURCE_KEYS if k != "deposits") + (
    "amount", "sale_price", "valuation", "documented_purchase_offers",
)

# Source keys holding a list of amounts rather than a single one.
LIST_SOURCE_KEYS = ("deposits",)


def money_sum(node):
    """Sum every monetary value anywhere in a nested structure."""
    total = Decimal("0")
    if isinstance(node, dict):
        for key, value in node.items():
            if key in LIST_SOURCE_KEYS and isinstance(value, list):
                total += sum(Decimal(str(v)) for v in value)
            elif key in MONEY_KEYS and isinstance(value, (int, float)):
                total += Decimal(str(value))
            else:
                total += money_sum(value)
    elif isinstance(node, list):
        for item in node:
            total += money_sum(item)
    return total


def fact_sources(normalized):
    """Total the documented funding components of one acquisition fact."""
    total = Decimal("0")
    for key in SOURCE_KEYS:
        if key not in normalized:
            continue
        value = normalized[key]
        if isinstance(value, list):
            total += sum(Decimal(str(v)) for v in value)
        elif isinstance(value, (int, float)):
            total += Decimal(str(value))
    return total


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "record_snapshot.json"
    with open(path, encoding="utf-8") as fh:
        record = json.load(fh)

    print(f"{'collection':<24} {'rows':>6}  {'money sum':>16}")
    print("-" * 50)
    for key in sorted(k for k in record if not k.startswith("_")):
        rows = record[key]
        print(f"{key:<24} {len(rows):>6}  {money_sum(rows):>16,.2f}")

    # Invariants the court package depends on directly. A partial acquisition
    # fact is a state the package is built to report, so the verifier reports it
    # too rather than failing on it.
    print()
    print("acquisition invariants:")
    for fact in record["acquisition_facts"]:
        nv = fact.get("normalized_value") or {}
        name = nv.get("property") or "<no property key>"
        sources = fact_sources(nv)
        raw_price = nv.get("sale_price")
        if raw_price is None:
            print(f"  {name:<32} price=  NOT IN RECORD "
                  f"sources={sources:>12,.2f} variance=  NOT COMPUTABLE")
            continue
        price = Decimal(str(raw_price))
        print(f"  {name:<32} price={price:>12,.2f} "
              f"sources={sources:>12,.2f} variance={sources - price:>12,.2f}")


if __name__ == "__main__":
    main()
