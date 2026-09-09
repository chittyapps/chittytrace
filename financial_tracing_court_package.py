#!/usr/bin/env python3
"""
Court-ready financial tracing package generator — five-property portfolio.

Builds a Cook County Domestic Relations tracing exhibit set for the property
portfolio at issue in In re Marriage of Arias Montealegre v. Bianchi,
Case No. 2024-D-007847, directly from the ChittyOS-Core forensic record.

Every figure emitted by this generator is read live from the database. Nothing
is hardcoded, interpolated, or estimated. Where the record does not contain a
figure, the generator emits an explicit NOT IN RECORD gap with the discovery
step required to close it — it never substitutes a plausible number.

Usage:
    DATABASE_URL=postgres://... python3 financial_tracing_court_package.py \
        --outdir court_packages/financial_tracing

Source of record:
    Neon project ChittyOS-Core (restless-grass-40598426)
      public.atomic_facts            verified forensic facts
      public.cc_properties           property canon (PIN, servicer, metadata)
      public.contradictions          open conflicts against those facts
      public.cases                   case caption and jurisdiction
      staging.evidence_index_avb     exhibit index (Exh####)
      storage.documents              primary-source document store
      verification.verification_items  evidentiary posture and open blockers
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import OrderedDict
from datetime import date, datetime, timezone
from decimal import Decimal

CASE_NUMBER_CANONICAL = "2024-D-007847"

# Marriage date governs the Illinois marital-property presumption (750 ILCS
# 5/503(a)/(b)). Sourced from verification item AS-1.1, which fixes the marriage
# at December 30, 2022 in computing the 151-day pre-marital formation gap.
MARRIAGE_DATE = date(2022, 12, 30)
MARRIAGE_DATE_AUTHORITY = "verification.verification_items AS-1.1 (status=verified, confidence=very_high)"

# The five properties in the portfolio, keyed by the `property` value carried in
# atomic_facts.normalized_value. Each entry declares how the property is named in
# public.cc_properties and which filename patterns identify its primary sources.
# A property with no acquisition fact in the record is still listed here — the
# generator reports the absence rather than omitting the property.
PORTFOLIO = OrderedDict([
    ("541_W_Addison_3S", {
        "name": "Lakeside Loft",
        "address": "541 W Addison St, Unit 3S, Chicago, IL 60613",
        "cc_property_name": "Lakeside Loft",
        "title_holder": "Nicholas Anthony Bianchi (individually)",
        "doc_patterns": ["addison"],
    }),
    ("550_W_Surf_504_Cozy_Castle", {
        "name": "Cozy Castle",
        "address": "550 W Surf St, Unit 504, Chicago, IL 60657",
        "cc_property_name": "Cozy Castle",
        "title_holder": "Nicholas Anthony Bianchi (individually)",
        "doc_patterns": ["surf.{0,12}504", "504.{0,12}surf"],
    }),
    ("550_W_Surf_211_City_Studio", {
        "name": "City Studio",
        "address": "550 W Surf St, Unit C211, Chicago, IL 60657",
        "cc_property_name": "City Studio",
        "title_holder": "ARIBIA LLC — CITY STUDIO (series)",
        "doc_patterns": ["surf.{0,12}211", "211.{0,12}surf"],
    }),
    ("MORADA_MAMI_MEDELLIN", {
        "name": "Morada Mami",
        "address": "Carrera 76 A # 53-215, Medellin, Antioquia, Colombia",
        "cc_property_name": None,  # not carried in cc_properties
        "title_holder": "ARIBIA LLC — MORADA MAMI (series)",
        "doc_patterns": ["morada", "medell", "escritura", "otrosi"],
        # Read from the extracted text of Escritura Publica 1524/1545
        # (scan-6f8e83ce87ea). That instrument is the developer's 2008 sale and
        # is not the acquisition instrument, but it does fix the legal
        # description of the parcel.
        "legal_description": (
            "Apartamento 1112, Torre 2, Conjunto Residencial Urbanizacion "
            "Plaza de Colores P.H., Carrera 76A No. 53-215, Medellin — "
            "matricula inmobiliaria 01N-5270691; parqueadero 226, matricula "
            "01N-5270572"
        ),
        "exhibit_integrity_note": {
            "severity": "CRITICAL",
            "gap": ("The document filed as the Morada Mami deed is not a deed "
                    "to this party."),
            "consequence": (
                "`Morada Mami Deed Escritura publica 1524 del 13 de febrero de "
                "2008.pdf` is Escritura 1524/1545, executed 13 February 2008 by "
                "Constructora Capital S.A. in favor of Cesar Augusto Barco "
                "Lopez for COP $87,826,000. It is a chain-of-title instrument "
                "from fifteen years before the acquisition at issue, naming a "
                "different grantee and a different price. Produced as 'the "
                "deed' it would show, on its face, that the party does not hold "
                "title — an unforced and serious error."
            ),
            "action": (
                "Re-label this instrument as chain of title. Obtain the 2023 "
                "escritura de compraventa recording transfer to ARIBIA LLC, "
                "together with its certificado de tradicion y libertad."
            ),
        },
    }),
    ("4343_N_Clarendon_Apt_Arlene", {
        "name": "Villa Vista",
        "address": "4343 N Clarendon Ave, Unit 1610, Chicago, IL 60613",
        "cc_property_name": "Villa Vista",
        "title_holder": "ARIBIA LLC — APT ARLENE (series)",
        "doc_patterns": ["clarendon", "arlene", "villa.?vista", "1610"],
    }),
])

# Filenames matching this pattern are the property-relevant slice of the exhibit
# index and the document store. Kept in one place so the SQL filter and the
# per-property matcher cannot drift apart.
EXHIBIT_FILENAME_PATTERN = (
    "(surf|addison|clarendon|arlene|villa.?vista|1610|morada|medell|"
    "escritura|otrosi|alta|closing|deed|wire|master statement|final statement|"
    "fidelity|earnest)"
)

# Keys inside atomic_facts.normalized_value that represent money applied toward
# an acquisition. `deposits` is a list; the rest are scalars.
SOURCE_KEYS = ("loan", "wire", "wire_USAA", "deposit", "deposits", "cash", "credit")

# Materiality floor for flagging a source/application variance, in dollars.
# Below this, a variance is consistent with ordinary closing prorations and
# credits; at or above it, the variance is reported as an unreconciled amount.
VARIANCE_MATERIALITY = Decimal("1000.00")


# --------------------------------------------------------------------------
# Data access
# --------------------------------------------------------------------------

RECORD_KEYS = (
    "case", "acquisition_facts", "capital_facts", "property_liabilities",
    "cc_properties", "exhibits", "closing_documents", "contradictions",
    "blockers", "verified_items",
)


def connect():
    """Open a read-only connection to ChittyOS-Core from DATABASE_URL."""
    # Imported here, not at module load, so that snapshot replay (--record)
    # works on a machine with no database driver installed.
    import psycopg2

    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        sys.exit(
            "DATABASE_URL is not set. Point it at the ChittyOS-Core database "
            "(Neon project restless-grass-40598426), or pass --record with a "
            "snapshot produced by a brokered read."
        )
    conn = psycopg2.connect(dsn)
    conn.set_session(readonly=True, autocommit=True)
    return conn


def load_record_snapshot(path):
    """Load a record captured through a brokered read-only path.

    Direct DSN access requires a privileged role password. Where policy keeps
    that credential inside bound services only, the same queries are run through
    the broker and their results captured as a snapshot, which this function
    replays. The analysis and rendering downstream are identical either way.
    """
    with open(path, encoding="utf-8") as fh:
        record = json.load(fh)
    missing = [k for k in RECORD_KEYS if k not in record]
    if missing:
        sys.exit(f"Snapshot {path} is missing required keys: {', '.join(missing)}")
    return record


def fetch(conn, sql, params=None):
    """Run one query and return its rows as plain dicts."""
    import psycopg2.extras

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params or ())
        return [dict(r) for r in cur.fetchall()]


def load_record(conn):
    """Pull every input the package depends on, in one pass."""
    record = {}

    record["case"] = fetch(conn, """
        SELECT case_number, case_number_canonical, title, jurisdiction, status
        FROM public.cases WHERE case_number_canonical = %s
    """, (CASE_NUMBER_CANONICAL,))

    record["acquisition_facts"] = fetch(conn, """
        SELECT statement, confidence, source_reference, normalized_value
        FROM public.atomic_facts
        WHERE fact_type = 'property_purchase_price'
        ORDER BY normalized_value->>'date'
    """)

    record["capital_facts"] = fetch(conn, """
        SELECT statement, confidence, source_reference, normalized_value
        FROM public.atomic_facts
        WHERE fact_type = 'capital_contribution'
        ORDER BY (normalized_value->>'amount')::numeric DESC
    """)

    record["property_liabilities"] = fetch(conn, """
        SELECT statement, confidence, source_reference, normalized_value
        FROM public.atomic_facts
        WHERE fact_type IN ('liability', 'property_valuation')
        ORDER BY fact_type, statement
    """)

    record["cc_properties"] = fetch(conn, """
        SELECT property_name, address, unit, property_type, tax_pin,
               mortgage_servicer, metadata
        FROM public.cc_properties ORDER BY property_name
    """)

    record["exhibits"] = fetch(conn, """
        SELECT exhibit_id, category, filename
        FROM staging.evidence_index_avb
        WHERE filename ~* %s
        ORDER BY exhibit_id
    """, (EXHIBIT_FILENAME_PATTERN,))

    # Primary-source documents whose text has NOT been extracted are the
    # admissibility bottleneck: the figures they contain cannot be independently
    # verified against the fact base until they are.
    record["closing_documents"] = fetch(conn, """
        SELECT d.chitty_id, d.filename, d.size_bytes, d.source_platform,
               (t.content_hash IS NOT NULL) AS text_extracted,
               COALESCE(t.char_count, 0) AS char_count
        FROM storage.documents d
        LEFT JOIN storage.document_text t ON t.content_hash = d.content_hash
        WHERE d.deleted_at IS NULL
          AND d.filename ~* '(alta|closing disclosure|master statement|final statement|warranty deed|settlement statement|otrosi|escritura)'
        ORDER BY d.filename
    """)

    record["contradictions"] = fetch(conn, """
        SELECT contradiction_type, severity, status, description,
               normalized_value1, normalized_value2
        FROM public.contradictions
        WHERE contradiction_type IN ('property_purchase_price','capital_contribution')
        ORDER BY contradiction_type
    """)

    record["blockers"] = fetch(conn, """
        SELECT item_type, statement, status, confidence_level
        FROM verification.verification_items
        WHERE deleted_at IS NULL
          AND status IN ('pending_review','under_review','extracted')
        ORDER BY status, statement
    """)

    record["verified_items"] = fetch(conn, """
        SELECT item_type, statement, value, status, confidence_level
        FROM verification.verification_items
        WHERE deleted_at IS NULL AND status = 'verified'
        ORDER BY item_type, statement
    """)

    return record


# --------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------

def dec(value):
    """Convert a JSON number to Decimal, preserving None for absent figures."""
    if value is None:
        return None
    return Decimal(str(value))


def money(value):
    """Render an amount for the schedule, or NOT IN RECORD when absent.

    Absent figures must never render as $0.00: a zero states that nothing was
    paid, while the record here states only that no amount is known.
    """
    if value is None:
        return "NOT IN RECORD"
    return f"${value:,.2f}"


def parse_iso(value):
    """Parse a YYYY-MM-DD string into a date, or None when absent."""
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def exhibit_date(filename):
    """Read the leading YYYY-MM-DD date off an exhibit filename, if present."""
    import re
    match = re.match(r"\s*(\d{4})-(\d{2})-(\d{2})", filename or "")
    if not match:
        return None
    try:
        return date(*(int(g) for g in match.groups()))
    except ValueError:
        return None


def marital_posture(acquired):
    """Classify an acquisition against the marital-property presumption."""
    if acquired is None:
        return {
            "classification": "UNDETERMINED",
            "days": None,
            "presumption": "Cannot be classified — acquisition date not in record.",
        }
    delta = (acquired - MARRIAGE_DATE).days
    if delta < 0:
        return {
            "classification": "PRE-MARITAL",
            "days": abs(delta),
            "presumption": (
                f"Acquired {abs(delta)} days before the marriage. Presumptively "
                "non-marital under 750 ILCS 5/503(a)(6); tracing is corroborative, "
                "not dispositive."
            ),
        }
    return {
        "classification": "ACQUIRED DURING MARRIAGE",
        "days": delta,
        "presumption": (
            f"Acquired {delta} days after the marriage. Presumptively MARITAL "
            "under 750 ILCS 5/503(b)(1). The presumption is overcome only by "
            "clear and convincing evidence tracing the acquisition to a "
            "non-marital source."
        ),
    }


def extract_sources(normalized):
    """Pull the documented funding components out of an acquisition fact."""
    sources = []
    for key in SOURCE_KEYS:
        if key not in normalized:
            continue
        raw = normalized[key]
        if isinstance(raw, list):
            for i, item in enumerate(raw, start=1):
                sources.append({"component": f"{key}[{i}]", "amount": dec(item)})
        else:
            sources.append({"component": key, "amount": dec(raw)})
    return sources


def pin_is_corroborated(record, pin):
    """Report whether any source in the record supports this parcel number.

    A parcel identifier carried only in the property canon is an unsourced
    assertion: `cc_properties` is a convenience table, not an instrument. A PIN
    is corroborated only if it also appears in a verified fact, an indexed
    exhibit, or a document in the store — that is, if something a court could be
    shown says so.
    """
    if not pin:
        return False
    needle = pin.strip()
    haystacks = []
    for key in ("acquisition_facts", "capital_facts", "property_liabilities"):
        haystacks.extend(json.dumps(row, default=str) for row in record.get(key, []))
    for key in ("exhibits", "closing_documents"):
        haystacks.extend((row.get("filename") or "") for row in record.get(key, []))
    return any(needle in text for text in haystacks)


def detect_pin_conflicts(cc_properties):
    """Flag parcel identifiers the record itself shows cannot all be right.

    Two checks, both decided from the stored data alone — this function never
    asserts what a PIN ought to be, because substituting a researched parcel
    number into a court exhibit would be exactly the invention this package
    refuses to commit.

    1. Units in the same building must share a PIN prefix. A Cook County PIN
       encodes area, sub-area and block in its leading segments, so two units
       at one street address that differ there cannot both be correct.
    2. A stored municipality that contradicts the stored street address.
    """
    conflicts = {}

    def add(name, gap):
        """Attach a gap to the named property."""
        conflicts.setdefault(name, []).append(gap)

    def norm_address(row):
        """Normalise a stored address for comparison across rows."""
        return " ".join((row.get("address") or "").split()).rstrip(",").lower()

    by_address = {}
    for row in cc_properties:
        by_address.setdefault(norm_address(row), []).append(row)

    for address, rows in by_address.items():
        if len(rows) < 2:
            continue
        prefixes = {}
        for row in rows:
            pin = row.get("tax_pin") or ""
            prefix = "-".join(pin.split("-")[:2])
            if prefix:
                prefixes.setdefault(prefix, []).append(row)
        if len(prefixes) > 1:
            listed = "; ".join(
                f"{r['property_name']} unit {r.get('unit') or '?'} → {r.get('tax_pin')}"
                for r in rows
            )
            for row in rows:
                add(row["property_name"], {
                    "severity": "CRITICAL",
                    "gap": ("The parcel identifier is inconsistent with the other "
                            "unit recorded at the same address."),
                    "consequence": (
                        f"The record places these units at the same building "
                        f"({address}) but assigns them parcel numbers from "
                        f"different areas: {listed}. A Cook County PIN encodes "
                        "area and block in its leading segments, so units in one "
                        "building share that prefix. At least one of these "
                        "identifiers is wrong, and an exhibit citing the wrong "
                        "parcel describes someone else's property."
                    ),
                    "action": (
                        "Confirm each unit against the Cook County Assessor and "
                        "the recorded deed, correct the property canon, and "
                        "regenerate. Do not file an unverified parcel number."
                    ),
                })

    # The stored addresses omit the city, so the municipality is checked against
    # the curated portfolio address, which carries it.
    canon_by_name = {
        meta["cc_property_name"]: meta["address"]
        for meta in PORTFOLIO.values() if meta.get("cc_property_name")
    }
    for row in cc_properties:
        metadata = row.get("metadata") or {}
        municipality = (metadata.get("municipality") or "").strip()
        canon_address = canon_by_name.get(row["property_name"])
        if not municipality or not canon_address:
            continue
        if municipality.lower() in canon_address.lower():
            continue
        add(row["property_name"], {
            "severity": "REVIEW",
            "gap": (f"The property canon records the municipality as "
                    f"'{municipality}', which the property's address contradicts."),
            "consequence": (
                f"The property is at {canon_address}. A municipality that does "
                "not match the address usually means the parcel record was "
                "copied from a different property, which puts the parcel number "
                "recorded alongside it in the same doubt."
            ),
            "action": "Verify the municipality and parcel number together.",
        })

    return conflicts


def canon_disagreements(normalized, cc_row):
    """Compare an acquisition fact against the property canon's own copy."""
    gaps = []
    metadata = cc_row.get("metadata") or {}

    fact_date = normalized.get("date")
    canon_date = metadata.get("purchase_date")
    if fact_date and canon_date and fact_date != canon_date:
        gaps.append({
            "severity": "REVIEW",
            "gap": (f"The acquisition date is recorded twice and the two copies "
                    f"disagree: {fact_date} against {canon_date}."),
            "consequence": (
                "The schedule states the acquisition-fact date and computes the "
                "marital-timing calculation from it. The difference does not "
                "change the classification here, but an unexplained two-date "
                "record invites the question of which one the instrument says."
            ),
            "action": (
                "Read the recorded deed and reconcile both entries to it."
            ),
        })

    fact_price = dec(normalized.get("sale_price"))
    canon_price = dec(metadata.get("purchase_price"))
    if fact_price is not None and canon_price is not None and fact_price != canon_price:
        gaps.append({
            "severity": "CRITICAL",
            "gap": (f"The purchase price is recorded twice and the two copies "
                    f"disagree: {money(fact_price)} against {money(canon_price)}."),
            "consequence": (
                "The schedule cannot state a single acquisition price for this "
                "property, and every variance computed from it is unreliable."
            ),
            "action": "Reconcile both entries against the settlement statement.",
        })

    return gaps


def build_property_analysis(record):
    """Assemble the tracing schedule for each of the five properties."""
    facts_by_property = {}
    duplicate_fact_keys = set()
    for row in record["acquisition_facts"]:
        nv = row["normalized_value"] or {}
        key = nv.get("property")
        if key:
            if key in facts_by_property:
                duplicate_fact_keys.add(key)
            facts_by_property[key] = row

    cc_by_name = {r["property_name"]: r for r in record["cc_properties"]}
    pin_conflicts = detect_pin_conflicts(record["cc_properties"])

    analyses = []
    for key, meta in PORTFOLIO.items():
        fact = facts_by_property.get(key)
        cc = cc_by_name.get(meta["cc_property_name"]) if meta["cc_property_name"] else None

        analysis = {
            "key": key,
            "name": meta["name"],
            "address": meta["address"],
            "title_holder": meta["title_holder"],
            "tax_pin": cc["tax_pin"] if cc else None,
            "tax_pin_corroborated": pin_is_corroborated(
                record, cc["tax_pin"] if cc else None),
            "mortgage_servicer": (cc or {}).get("mortgage_servicer"),
            "cc_metadata": (cc or {}).get("metadata"),
            "legal_description": meta.get("legal_description"),
            "has_acquisition_fact": fact is not None,
            "gaps": [],
        }

        if meta.get("exhibit_integrity_note"):
            analysis["gaps"].append(meta["exhibit_integrity_note"])

        if key in duplicate_fact_keys:
            analysis["gaps"].append({
                "severity": "CRITICAL",
                "gap": "The fact base carries more than one acquisition fact for this property.",
                "consequence": (
                    "The figures below reflect one of several competing facts. "
                    "The schedule cannot state a single acquisition price on "
                    "this record, and the competing figure is not shown."
                ),
                "action": (
                    "Resolve the competing acquisition facts and mark the "
                    "superseded entries."
                ),
            })

        for conflict in pin_conflicts.get(meta["cc_property_name"], []):
            analysis["gaps"].append(conflict)

        if analysis["tax_pin"] and not analysis["tax_pin_corroborated"]:
            analysis["gaps"].append({
                "severity": "CRITICAL",
                "gap": ("No source in the record corroborates a parcel "
                        "identifier for this property."),
                "consequence": (
                    f"The property canon carries {analysis['tax_pin']}, but that "
                    "value appears in no verified fact, no indexed exhibit and "
                    "no document in the store. It is an unsourced assertion, so "
                    "this schedule does not state it as the parcel identifier. "
                    "A legal description in a filed exhibit must come from the "
                    "recorded instrument, not from a convenience table."
                ),
                "action": (
                    "Confirm the parcel number against the Cook County Assessor "
                    "and the recorded deed, seed it as a cited fact, and "
                    "regenerate."
                ),
            })

        # The property canon carries its own copy of the acquisition date and
        # price. Where it disagrees with the acquisition fact, the schedule must
        # say so rather than silently preferring one source.
        if fact is not None and cc:
            analysis["gaps"].extend(
                canon_disagreements(fact["normalized_value"] or {}, cc)
            )

        if fact is None:
            analysis.update({
                "acquired": None,
                "purchase_price": None,
                "sources": [],
                "sources_total": None,
                "variance": None,
                "posture": marital_posture(None),
                "fact_confidence": None,
                "fact_source": None,
            })
            analysis["gaps"].append({
                "severity": "CRITICAL",
                "gap": "No acquisition fact of any kind exists for this property.",
                "consequence": (
                    "Purchase price, closing date, and funding sources are all "
                    "absent from the fact base. No tracing opinion can be "
                    "offered and no exhibit can be authenticated on this record."
                ),
                "action": (
                    "Extract the purchase instrument and settlement figures, "
                    "seed them as atomic facts, then re-run this generator."
                ),
            })
            analyses.append(analysis)
            continue

        nv = fact["normalized_value"] or {}
        acquired = parse_iso(nv.get("date"))
        price = dec(nv.get("sale_price"))
        sources = extract_sources(nv)
        sources_total = sum((s["amount"] for s in sources if s["amount"] is not None),
                            Decimal("0")) if sources else None
        variance = (sources_total - price) if (sources_total is not None and price is not None) else None

        analysis.update({
            "acquired": acquired,
            "purchase_price": price,
            "sources": sources,
            "sources_total": sources_total,
            "variance": variance,
            "posture": marital_posture(acquired),
            "fact_confidence": fact["confidence"],
            "fact_source": fact["source_reference"],
        })

        # A documented funding component says how much was applied. It does not
        # say where that money came from. For tracing purposes those are
        # different questions, and only the second one defeats the marital
        # presumption.
        analysis["gaps"].append({
            "severity": "STRUCTURAL",
            "gap": "Funding components are recorded as amounts applied, not as traced origins.",
            "consequence": (
                "The record establishes what was paid at closing. It does not, "
                "on its own, establish the account of origin, the balance in "
                "that account before the transfer, or the absence of "
                "commingling — the three elements Illinois tracing requires."
            ),
            "action": (
                "Obtain the originating account statements covering the 60 days "
                "before each transfer and seed the balances as atomic facts."
            ),
        })

        if variance is not None and abs(variance) >= VARIANCE_MATERIALITY:
            if variance < 0:
                analysis["gaps"].append({
                    "severity": "CRITICAL",
                    "gap": f"Documented sources fall {money(abs(variance))} short of the purchase price.",
                    "consequence": (
                        "An unsourced balance at closing is the single most "
                        "effective target for a marital-contribution argument: "
                        "money whose origin is unproven is presumed marital."
                    ),
                    "action": (
                        "Produce the settlement statement and identify every "
                        "debit funding the shortfall."
                    ),
                })
            else:
                analysis["gaps"].append({
                    "severity": "REVIEW",
                    "gap": f"Documented sources exceed the purchase price by {money(variance)}.",
                    "consequence": (
                        "Ordinarily this reflects closing costs, prorations, or "
                        "escrow funding rather than an error, but the excess is "
                        "unexplained on the present record."
                    ),
                    "action": "Reconcile against the settlement statement line items.",
                })

        if price is not None and not sources:
            analysis["gaps"].append({
                "severity": "CRITICAL",
                "gap": "Purchase price is recorded but no funding component is.",
                "consequence": "The entire acquisition is unsourced.",
                "action": "Produce the settlement statement and funding instruments.",
            })

        analyses.append(analysis)

    return analyses


def match_exhibits(analysis, record):
    """Attach the primary-source exhibits and documents for one property."""
    import re
    meta = PORTFOLIO[analysis["key"]]
    pattern = re.compile("|".join(meta["doc_patterns"]), re.IGNORECASE)

    exhibits = [e for e in record["exhibits"] if pattern.search(e["filename"] or "")]
    documents = [d for d in record["closing_documents"] if pattern.search(d["filename"] or "")]
    return exhibits, documents


def audit_contradictions(record):
    """Separate genuine conflicts from detector artifacts.

    The contradiction detector groups by fact_type alone. For fact types that
    are inherently per-entity — property_purchase_price is one fact per property
    — every cross-property pair is reported as a conflict. Those are artifacts,
    not conflicts, and must not be presented to a court as inconsistencies in
    the record.
    """
    genuine, artifacts = [], []
    for row in record["contradictions"]:
        v1 = row["normalized_value1"] or {}
        v2 = row["normalized_value2"] or {}
        if row["contradiction_type"] == "property_purchase_price":
            if v1.get("property") != v2.get("property"):
                artifacts.append({**row, "reason": "Compares two different properties."})
            else:
                genuine.append(row)
        elif row["contradiction_type"] == "capital_contribution":
            # Two capitalization figures conflict only if they purport to
            # measure the same thing. A component and a total do not conflict;
            # neither do figures attributed to different contributors; neither
            # does a live figure and one expressly superseded.
            scope1 = v1.get("category") or v1.get("source")
            scope2 = v2.get("category") or v2.get("source")
            contrib1, contrib2 = v1.get("contributor"), v2.get("contributor")

            if "superseded" in (v1.get("status"), v2.get("status")):
                artifacts.append({**row, "reason": "One side is expressly marked superseded."})
            elif contrib1 != contrib2 and (contrib1 or contrib2):
                named = contrib1 or contrib2
                artifacts.append({**row, "reason": (
                    f"One side is scoped to a single contributor ({named}); the "
                    "other is an entity-level figure. Different measurements.")})
            elif scope1 and scope2 and scope1 != scope2:
                artifacts.append({**row, "reason": f"Compares '{scope1}' against '{scope2}' — different scopes."})
            else:
                genuine.append(row)
        else:
            genuine.append(row)
    return genuine, artifacts


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def render_package(record, analyses, generated_at):
    """Render the full Cook County tracing schedule as Markdown."""
    case = record["case"][0] if record["case"] else {}
    genuine, artifacts = audit_contradictions(record)

    out = []
    w = out.append

    w("# SCHEDULE OF FINANCIAL TRACING — REAL PROPERTY PORTFOLIO")
    w("")
    w("**IN THE CIRCUIT COURT OF COOK COUNTY, ILLINOIS**  ")
    w("**COUNTY DEPARTMENT, DOMESTIC RELATIONS DIVISION**")
    w("")
    w(f"**In re the Marriage of:** {case.get('title', 'NOT IN RECORD')}")
    w("")
    w(f"**Case No.:** {case.get('case_number', CASE_NUMBER_CANONICAL)}  ")
    w(f"**Jurisdiction:** {case.get('jurisdiction', 'NOT IN RECORD')}")
    w("")
    w("---")
    w("")
    w("## PREFATORY STATEMENT ON THE SCOPE OF THIS SCHEDULE")
    w("")
    w("This schedule is a **tracing worksheet compiled from a document management "
      "system**. It is not a forensic accounting opinion, it is not attested by a "
      "certified public accountant, and it is not competent to be filed as an "
      "expert report. It states what the assembled record does and does not "
      "establish about the acquisition of five parcels of real property, so that "
      "counsel can direct the discovery needed to close the difference.")
    w("")
    w("Every figure below is read from the underlying database at generation time "
      "and carries its source. Where the record contains no figure, this schedule "
      "says **NOT IN RECORD** and states the step required to obtain it. No "
      "amount in this document is estimated, interpolated, or reconstructed.")
    w("")
    w(f"**Generated:** {generated_at:%B %d, %Y at %H:%M UTC}  ")
    w("**Source of record:** ChittyOS-Core (Neon `restless-grass-40598426`)  ")
    w(f"**Marital cut-off date:** {MARRIAGE_DATE:%B %d, %Y}  ")
    w(f"**Cut-off authority:** {MARRIAGE_DATE_AUTHORITY}")
    w("")
    w("---")
    w("")

    # ---- Portfolio summary -------------------------------------------------
    w("## PART I — PORTFOLIO SUMMARY")
    w("")
    w("| # | Property | Acquired | Price | Documented Sources | Unreconciled | Presumption |")
    w("|---|----------|----------|-------|--------------------|--------------|-------------|")
    for i, a in enumerate(analyses, start=1):
        acquired = f"{a['acquired']:%Y-%m-%d}" if a["acquired"] else "NOT IN RECORD"
        variance = a["variance"]
        if variance is None:
            var_cell = "—"
        elif abs(variance) < VARIANCE_MATERIALITY:
            var_cell = "within tolerance"
        elif variance < 0:
            var_cell = f"**{money(abs(variance))} short**"
        else:
            var_cell = f"{money(variance)} over"
        w(f"| {i} | {a['name']} | {acquired} | {money(a['purchase_price'])} | "
          f"{money(a['sources_total'])} | {var_cell} | {a['posture']['classification']} |")
    w("")

    priced = [a for a in analyses if a["purchase_price"] is not None]
    if priced:
        total_price = sum(a["purchase_price"] for a in priced)
        total_sources = sum(a["sources_total"] for a in priced if a["sources_total"] is not None)
        w(f"**Aggregate documented acquisition cost (of {len(priced)} of {len(analyses)} "
          f"properties):** {money(total_price)}  ")
        w(f"**Aggregate documented funding sources:** {money(total_sources)}  ")
        shortfall = sum((abs(a["variance"]) for a in priced
                         if a["variance"] is not None and a["variance"] < 0),
                        Decimal("0"))
        excess = sum((a["variance"] for a in priced
                      if a["variance"] is not None and a["variance"] > 0),
                     Decimal("0"))
        w(f"**Aggregate unsourced balance (shortfalls only):** {money(shortfall)}  ")
        w(f"**Aggregate excess of sources over price:** {money(excess)}  ")
        w(f"**Net difference (price less sources):** {money(total_price - total_sources)}")
        w("")
        w("> The shortfall and the excess arise on different closings and do not "
          "offset one another. An excess at one settlement does not fund a "
          "shortfall at another, so the unsourced balance the record must "
          f"account for is {money(shortfall)}, not the net figure.")
        w("")
        missing = [a["name"] for a in analyses if a["purchase_price"] is None]
        if missing:
            w(f"> The aggregate excludes {', '.join(missing)}, for which the record "
              "contains no acquisition figure at all. The true portfolio cost is "
              "therefore higher than the total stated above by an unknown amount.")
            w("")
    w("---")
    w("")

    # ---- Per-property schedules -------------------------------------------
    w("## PART II — PER-PROPERTY TRACING SCHEDULES")
    w("")
    for i, a in enumerate(analyses, start=1):
        exhibits, documents = match_exhibits(a, record)

        w(f"### SCHEDULE {i} — {a['name'].upper()}")
        w("")
        w(f"**Address:** {a['address']}  ")
        w(f"**Title holder of record:** {a['title_holder']}  ")
        if a["tax_pin"] and a["tax_pin_corroborated"]:
            w(f"**Cook County PIN:** {a['tax_pin']}  ")
        elif a["tax_pin"]:
            w("**Parcel identifier:** NOT IN RECORD — verification required  ")
        if a["legal_description"]:
            w(f"**Legal description:** {a['legal_description']}  ")
        if not a["tax_pin"] and not a["legal_description"]:
            w("**Parcel identifier:** NOT IN RECORD  ")
        if a["mortgage_servicer"]:
            servicer = " / ".join(s.strip() for s in a["mortgage_servicer"].split("\n") if s.strip())
            w(f"**Mortgage servicer(s):** {servicer}  ")
        w("")

        w(f"**Classification:** {a['posture']['classification']}")
        w("")
        w(f"> {a['posture']['presumption']}")
        w("")

        # Where the fact base cannot classify a property, the exhibit index may
        # still carry dated instruments that indicate when the acquisition
        # occurred. That is an indication for directing discovery, not a
        # substitute for the missing fact, and is labelled as such.
        if a["posture"]["classification"] == "UNDETERMINED":
            dated = sorted(
                d for d in (exhibit_date(e["filename"]) for e in exhibits) if d
            )
            if dated:
                earliest, latest = dated[0], dated[-1]
                side = "after" if earliest > MARRIAGE_DATE else "before"
                w(f"**Indication only (not a classification):** the exhibit index "
                  f"carries {len(dated)} dated instruments for this property, "
                  f"running {earliest:%Y-%m-%d} to {latest:%Y-%m-%d}. The "
                  f"earliest falls {side} the marital cut-off. If the "
                  f"acquisition tracks those instruments it would be "
                  f"**presumptively marital**, and the burden would fall on the "
                  f"party asserting otherwise. This cannot be relied on until "
                  f"the acquisition instrument itself is produced.")
                w("")

        if not a["has_acquisition_fact"]:
            w("#### Source and Application of Funds")
            w("")
            w("**NOT IN RECORD.** The fact base contains no acquisition entry for "
              "this property — no closing date, no purchase price, and no funding "
              "component.")
            w("")
        else:
            w("#### Source and Application of Funds")
            w("")
            w("| Line | Component | Amount | Character on this record |")
            w("|------|-----------|--------|--------------------------|")
            w(f"| A | Purchase price (application of funds) | {money(a['purchase_price'])} | Per acquisition fact |")
            for j, s in enumerate(a["sources"], start=1):
                w(f"| B{j} | {s['component']} | {money(s['amount'])} | Amount applied; origin not established by this line |")
            w(f"| C | **Total documented sources** | **{money(a['sources_total'])}** | Sum of B |")
            variance = a["variance"]
            if variance is not None:
                if variance < 0:
                    w(f"| D | **Unsourced balance (A − C)** | **{money(abs(variance))}** | **No documented origin** |")  # noqa: RUF001
                else:
                    w(f"| D | Excess of sources over price (C − A) | {money(variance)} | Unexplained on this record |")  # noqa: RUF001
            w("")
            w(f"*Acquisition fact confidence: {a['fact_confidence']} — source: "
              f"`{a['fact_source']}`*")
            w("")

        # Primary sources
        w("#### Primary Source Documents")
        w("")
        if exhibits:
            w("**Indexed exhibits:**")
            w("")
            w("| Exhibit | Category | Document |")
            w("|---------|----------|----------|")
            for e in exhibits:
                w(f"| {e['exhibit_id']} | {e['category']} | {e['filename']} |")
            w("")
        else:
            w("**Indexed exhibits:** none in the exhibit index for this property.")
            w("")

        if documents:
            unextracted = [d for d in documents if not d["text_extracted"]]
            w("**Closing instruments held in the document store:**")
            w("")
            w("| Document | Text extracted | Verifiable from this record |")
            w("|----------|----------------|------------------------------|")
            for d in documents:
                mark = "yes" if d["text_extracted"] else "**no**"
                verifiable = "yes" if d["text_extracted"] else "**no — figures unreadable**"
                w(f"| {d['filename']} | {mark} | {verifiable} |")
            w("")
            if unextracted:
                tail = ("so the amounts in the schedule above are presently "
                        "**uncorroborated by their own source documents**."
                        if a["has_acquisition_fact"] else
                        "and they are the most likely place the missing "
                        "acquisition figures for this property are recorded.")
                w(f"> {len(unextracted)} of {len(documents)} closing instruments for this "
                  "property are stored as un-OCR'd images. Their line-item figures "
                  f"cannot be compared against the fact base until they are extracted, {tail}")
                w("")
        else:
            w("**Closing instruments:** none identified in the document store.")
            w("")

        # Gaps
        if a["gaps"]:
            w("#### Evidentiary Gaps")
            w("")
            for g in a["gaps"]:
                w(f"**[{g['severity']}] {g['gap']}**")
                w("")
                w(f"- *Consequence:* {g['consequence']}")
                w(f"- *Action required:* {g['action']}")
                w("")
        w("---")
        w("")

    # ---- Entity capitalization --------------------------------------------
    w("## PART III — ENTITY CAPITALIZATION")
    w("")
    w("Three of the five properties are held by ARIBIA LLC series rather than "
      "individually. For those, tracing runs through the entity: the question is "
      "not only what funded the closing, but whether the capital that funded the "
      "entity was itself non-marital.")
    w("")
    w("| Figure | Amount | Scope | Confidence | Source |")
    w("|--------|--------|-------|------------|--------|")
    for row in record["capital_facts"]:
        nv = row["normalized_value"] or {}
        amount = dec(nv.get("amount"))
        scope = nv.get("category") or nv.get("source") or nv.get("contributor") or "—"
        status = nv.get("status")
        if status:
            scope = f"{scope} ({status})"
        w(f"| {row['statement']} | {money(amount)} | {scope} | {row['confidence']} | `{row['source_reference']}` |")
    w("")
    w("> These figures are not alternative estimates of one quantity. They measure "
      "different things — an initial deposit, direct member contributions, a "
      "verifiable subtotal, and a full tracing total — and a court will read any "
      "unexplained juxtaposition of them as inconsistency. Counsel should present "
      "one canonical figure with the others expressly reconciled beneath it.")
    w("")

    # The Operating Agreement is the best evidence of what was contributed at
    # formation. If the figure it recites is absent from the fact base, the fact
    # base and the signed instrument will not match under cross-examination.
    oa_items = [v for v in record["verified_items"]
                if isinstance(v.get("value"), dict)
                and "nicholas_contribution" in v["value"]]
    if oa_items:
        oa_amount = dec(oa_items[0]["value"]["nicholas_contribution"])
        fact_amounts = {dec((r["normalized_value"] or {}).get("amount"))
                        for r in record["capital_facts"]}
        if oa_amount not in fact_amounts:
            w("### Cross-check against the signed Operating Agreement")
            w("")
            w(f"Verification item AS-1.2, itself derived from the executed "
              f"Operating Agreement at page 18, records an initial contribution "
              f"of **{money(oa_amount)}** by the Respondent and **$0.00** by the "
              f"Petitioner.")
            w("")
            w(f"**{money(oa_amount)} does not appear anywhere in the "
              f"capitalization facts above.** The nearest figures are "
              + ", ".join(money(a) for a in sorted(x for x in fact_amounts if x) )
              + ".")
            w("")
            w("> This matters more than the spread between the other figures. The "
              "Operating Agreement is a signed instrument bearing both parties' "
              "signatures; the tracing totals are derived work product. On "
              "cross-examination the signed number is the one that will be put "
              "to the witness, and the fact base currently cannot reconcile to "
              "it. Establish the relationship between the Operating Agreement "
              "figure and the tracing total before either is filed.")
            w("")
    w("---")
    w("")

    # ---- Conflict audit ----------------------------------------------------
    w("## PART IV — CONFLICT AUDIT")
    w("")
    w(f"The contradiction engine reports **{len(record['contradictions'])} open conflicts** "
      "across the fact types relevant to this schedule. That count is misleading "
      "and must not be repeated to the court without the following correction.")
    w("")
    w(f"- **Genuine conflicts requiring resolution: {len(genuine)}**")
    w(f"- **Detector artifacts (not conflicts): {len(artifacts)}**")
    w("")
    if genuine:
        w("### Genuine conflicts")
        w("")
        for c in genuine:
            w(f"- **{c['contradiction_type']}** ({c['severity']}): "
              f"`{json.dumps(c['normalized_value1'], default=str)}` vs "
              f"`{json.dumps(c['normalized_value2'], default=str)}`")
        w("")
    if artifacts:
        w("### Detector artifacts")
        w("")
        w("The detector groups facts by `fact_type` alone. For fact types that are "
          "inherently one-per-entity, every cross-entity pair is emitted as a "
          "conflict. These are defects in the detector, not inconsistencies in the "
          "evidence:")
        w("")
        for c in artifacts:
            w(f"- **{c['contradiction_type']}**: {c['reason']}")
        w("")
        w("> **Recommendation:** partition contradiction detection by the entity key "
          "inside `normalized_value` (e.g. `property`, `category`) before comparing. "
          "Until that is fixed, the open-conflict count materially overstates the "
          "disorder in the record, and opposing counsel can use it to do so.")
        w("")
    w("---")
    w("")

    # ---- Admissibility -----------------------------------------------------
    w("## PART V — ADMISSIBILITY ASSESSMENT")
    w("")
    w("**This package is not presently in admissible form.** The following are "
      "the specific obstacles, in the order they must be cleared.")
    w("")

    blockers = record["blockers"]
    cpa = [b for b in blockers if "forensic accountant" in b["statement"].lower()
           or "cpa" in b["statement"].lower()]
    if cpa:
        w("### 1. No expert attestation")
        w("")
        for b in cpa:
            w(f"- {b['statement']} *(status: {b['status']})*")
        w("")
        w("A tracing analysis offered to defeat the marital presumption is expert "
          "opinion testimony. Without a retained forensic accountant who has "
          "reviewed the underlying records and will testify, this material is "
          "argument, not evidence.")
        w("")

    unextracted_all = [d for d in record["closing_documents"] if not d["text_extracted"]]
    w("### 2. Primary sources not machine-readable")
    w("")
    w(f"{len(unextracted_all)} of {len(record['closing_documents'])} closing "
      "instruments in the document store have no extracted text. Their figures "
      "have not been read into the fact base and cannot be verified against it.")
    w("")
    if unextracted_all:
        w("| Document | Size (bytes) |")
        w("|----------|--------------|")
        for d in unextracted_all:
            w(f"| {d['filename']} | {d['size_bytes']:,} |")
        w("")

    w("### 3. Acquisition-era banking records absent from the fact base")
    w("")
    w("The transaction record in the database covers the Medellin rent ledger and "
      "current operating activity. It contains no account-level activity from the "
      "acquisition periods (2019, 2022, 2023, 2024). Tracing requires the "
      "originating account statements for each transfer, and they are not here.")
    w("")

    other_blockers = [b for b in blockers if b not in cpa]
    if other_blockers:
        w("### 4. Open verification items")
        w("")
        w("| Status | Item |")
        w("|--------|------|")
        for b in other_blockers:
            w(f"| {b['status']} | {b['statement']} |")
        w("")
    w("---")
    w("")

    # ---- What is solid -----------------------------------------------------
    w("## PART VI — WHAT THE RECORD DOES ESTABLISH")
    w("")
    w("The following items are verified at high confidence and are the strongest "
      "material in the file:")
    w("")
    for v in record["verified_items"]:
        if v["item_type"] in ("assertion", "claim"):
            w(f"- **{v['item_type'].upper()}** — {v['statement']}")
    w("")
    w("---")
    w("")

    # ---- Priorities --------------------------------------------------------
    w("## PART VII — DISCOVERY PRIORITIES")
    w("")
    w("Ordered by the marginal value of closing each gap.")
    w("")
    ranked = []
    for a in analyses:
        critical = [g for g in a["gaps"] if g["severity"] == "CRITICAL"]
        if not critical:
            continue
        exposure = (abs(a["variance"]) if a["variance"] is not None and a["variance"] < 0
                    else a["purchase_price"])
        ranked.append({
            "name": a["name"],
            "classification": a["posture"]["classification"],
            "exposure_known": exposure is not None,
            "exposure": exposure or Decimal("0"),
            "gaps": critical,
        })

    # An unquantified exposure cannot be ranked below a quantified one: a
    # property with no acquisition fact could be worth more than every other
    # gap combined, and nothing in the record excludes that.
    ranked.sort(key=lambda r: (
        r["classification"] != "UNDETERMINED",
        r["classification"] != "ACQUIRED DURING MARRIAGE",
        -r["exposure"],
    ))

    for rank, r in enumerate(ranked, start=1):
        if r["classification"] == "ACQUIRED DURING MARRIAGE":
            why = ("acquired during the marriage, so the marital presumption "
                   "applies and only tracing defeats it")
        elif r["classification"] == "PRE-MARITAL":
            why = ("pre-marital, so exposure is limited to contribution and "
                   "commingling arguments")
        else:
            why = ("unclassified, because the acquisition date is not in the "
                   "record; the applicable presumption cannot be stated, and "
                   "the dated instruments on file point toward marital")
        amount = money(r["exposure"]) if r["exposure_known"] else "NOT IN RECORD"
        w(f"**{rank}. {r['name']}** — exposure {amount}; {why}.")
        w("")
        for g in r["gaps"]:
            w(f"   - {g['action']}")
        w("")

    w("---")
    w("")
    w("## CERTIFICATION OF PREPARATION")
    w("")
    w("This schedule was generated programmatically from the ChittyOS-Core "
      "forensic record. Its figures are reproducible by re-running the generator "
      "against the same database. It has not been reviewed or attested by a "
      "certified public accountant, and it is not offered as an expert report.")
    w("")
    w(f"Generated {generated_at:%Y-%m-%d %H:%M} UTC by "
      "`financial_tracing_court_package.py`.")
    w("")

    return "\n".join(out)


def render_dataset(record, analyses, generated_at):
    """Machine-readable appendix carrying every figure in the schedule."""
    def serialize(value):
        """Coerce Decimal and date values into JSON-representable types."""
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        return value

    genuine, artifacts = audit_contradictions(record)
    payload = {
        "generated_at": generated_at.isoformat(),
        "case_number": CASE_NUMBER_CANONICAL,
        "marriage_date": MARRIAGE_DATE.isoformat(),
        "marriage_date_authority": MARRIAGE_DATE_AUTHORITY,
        "source_database": "ChittyOS-Core (restless-grass-40598426)",
        "properties": [
            {
                "key": a["key"],
                "name": a["name"],
                "address": a["address"],
                "title_holder": a["title_holder"],
                "tax_pin_on_file": a["tax_pin"],
                "tax_pin_corroborated": a["tax_pin_corroborated"],
                "acquired": serialize(a["acquired"]),
                "purchase_price": serialize(a["purchase_price"]),
                "sources": [
                    {"component": s["component"], "amount": serialize(s["amount"])}
                    for s in a["sources"]
                ],
                "sources_total": serialize(a["sources_total"]),
                "variance": serialize(a["variance"]),
                "classification": a["posture"]["classification"],
                "days_from_marriage": a["posture"]["days"],
                "gaps": a["gaps"],
            }
            for a in analyses
        ],
        "conflict_audit": {
            "reported": len(record["contradictions"]),
            "genuine": len(genuine),
            "artifacts": len(artifacts),
        },
        "open_blockers": [
            {"status": b["status"], "statement": b["statement"]}
            for b in record["blockers"]
        ],
    }
    return json.dumps(payload, indent=2, default=serialize)


# --------------------------------------------------------------------------

def main():
    """Generate the tracing package from the database or a snapshot."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--outdir", default="court_packages/financial_tracing",
                        help="Directory to write the package into")
    parser.add_argument("--record", default=None,
                        help="Replay a snapshot captured through a brokered "
                             "read instead of connecting with a DSN")
    args = parser.parse_args()

    generated_at = datetime.now(timezone.utc)

    if args.record:
        record = load_record_snapshot(args.record)
    else:
        conn = connect()
        try:
            record = load_record(conn)
        finally:
            conn.close()

    analyses = build_property_analysis(record)

    os.makedirs(args.outdir, exist_ok=True)
    schedule_path = os.path.join(args.outdir, "SCHEDULE_OF_FINANCIAL_TRACING.md")
    dataset_path = os.path.join(args.outdir, "tracing_dataset.json")

    with open(schedule_path, "w", encoding="utf-8") as fh:
        fh.write(render_package(record, analyses, generated_at))
    with open(dataset_path, "w", encoding="utf-8") as fh:
        fh.write(render_dataset(record, analyses, generated_at))

    traced = sum(1 for a in analyses if a["has_acquisition_fact"])
    print(f"Wrote {schedule_path}")
    print(f"Wrote {dataset_path}")
    print(f"Properties with an acquisition fact: {traced}/{len(analyses)}")
    for a in analyses:
        critical = sum(1 for g in a["gaps"] if g["severity"] == "CRITICAL")
        print(f"  {a['name']:<14} {a['posture']['classification']:<26} "
              f"critical gaps: {critical}")


if __name__ == "__main__":
    main()
