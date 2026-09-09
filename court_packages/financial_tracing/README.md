# Financial Tracing Court Package — Five-Property Portfolio

Court-ready tracing schedule for the real property at issue in
*Arias Montealegre v. Bianchi*, Cook County Case No. 2024-D-007847.

## Files

| File | What it is |
|------|------------|
| `SCHEDULE_OF_FINANCIAL_TRACING.md` | The generated schedule. Regenerate; do not hand-edit. |
| `tracing_dataset.json` | Machine-readable appendix carrying every figure in the schedule. |
| `record_snapshot.json` | Input record captured from ChittyOS-Core. |
| `verify_record_snapshot.py` | Recomputes row counts and money sums from the snapshot, for comparison against the database. |
| `verify_record_snapshot.sql` | The counterpart aggregation to run against the database. |

The generator is `../../financial_tracing_court_package.py`.

## Regenerating

Against the live database:

```bash
pip install psycopg2-binary   # only needed for the live path
DATABASE_URL=<ChittyOS-Core> python3 financial_tracing_court_package.py \
    --outdir court_packages/financial_tracing
```

Replaying the captured snapshot, which needs neither a credential nor a
database driver — the `psycopg2` import is deferred into the live path:

```bash
python3 financial_tracing_court_package.py \
    --record court_packages/financial_tracing/record_snapshot.json \
    --outdir court_packages/financial_tracing
```

The snapshot exists because a direct DSN carries a privileged role password.
Capturing the same queries through the brokered read path keeps that credential
inside bound services, per the Credential Access Contract. The trade is only
safe if the snapshot is provably faithful, so verify it:

```bash
cd court_packages/financial_tracing && python3 verify_record_snapshot.py
```

That reads the snapshot only. The proof is the comparison: run
`verify_record_snapshot.sql` against ChittyOS-Core and diff its row counts and
money sums against what the script prints. As captured on 2026-09-09 these
matched exactly:

| Collection | Rows | Money sum |
|------------|------|-----------|
| acquisition_facts | 4 | 1,185,359.14 |
| capital_facts | 6 | 1,702,362.98 |
| property_liabilities | 11 | 1,012,867.49 |
| cc_properties | 4 | — |
| exhibits | 57 | — |
| closing_documents | 33 | — |
| contradictions | 21 | — |
| blockers | 13 | — |
| verified_items | 20 | — |

## Standing rule for this package

No figure is ever estimated, interpolated, or reconstructed. Where the record
holds no number, the schedule says **NOT IN RECORD** and states the discovery
step that would obtain it. A tracing schedule that guesses is worse than no
schedule at all, because it can be impeached.
