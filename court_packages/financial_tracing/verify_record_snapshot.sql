-- Counterpart aggregation for verify_record_snapshot.py.
--
-- Run this read-only against ChittyOS-Core (Neon restless-grass-40598426) and
-- diff its output against what verify_record_snapshot.py prints for the same
-- snapshot. Matching row counts and money sums establish that the snapshot is a
-- faithful copy of the record; any transcription error large enough to change a
-- figure in the court package will move one of these numbers.
--
-- The `money` column is 0 for collections that carry no independent monetary
-- figure of their own. A row count alone does NOT establish that such a
-- collection is faithful — an altered value would pass unnoticed — so the
-- second query below digests the cc_properties field values the generator
-- actually consumes. Run both, and compare both against the script's output.

SELECT 'acquisition_facts' AS collection, count(*) AS rows,
       sum( COALESCE((normalized_value->>'sale_price')::numeric, 0)
          + COALESCE((normalized_value->>'loan')::numeric, 0)
          + COALESCE((normalized_value->>'wire')::numeric, 0)
          + COALESCE((normalized_value->>'wire_USAA')::numeric, 0)
          + COALESCE((normalized_value->>'deposit')::numeric, 0)
          + COALESCE((normalized_value->>'cash')::numeric, 0)
          + COALESCE((normalized_value->>'credit')::numeric, 0)
          + COALESCE((SELECT sum(x::numeric)
                      FROM jsonb_array_elements_text(normalized_value->'deposits') x), 0)
          ) AS money
FROM public.atomic_facts
WHERE fact_type = 'property_purchase_price'

UNION ALL
SELECT 'capital_facts', count(*),
       sum(COALESCE((normalized_value->>'amount')::numeric, 0))
FROM public.atomic_facts
WHERE fact_type = 'capital_contribution'

UNION ALL
SELECT 'property_liabilities', count(*),
       sum( COALESCE((normalized_value->>'amount')::numeric, 0)
          + COALESCE((normalized_value->>'valuation')::numeric, 0)
          + COALESCE((normalized_value->>'documented_purchase_offers')::numeric, 0))
FROM public.atomic_facts
WHERE fact_type IN ('liability', 'property_valuation')

UNION ALL
SELECT 'case', count(*), 0 FROM public.cases
WHERE case_number_canonical = '2024-D-007847'

UNION ALL
SELECT 'cc_properties', count(*), 0 FROM public.cc_properties

UNION ALL
SELECT 'exhibits', count(*), 0 FROM staging.evidence_index_avb
WHERE filename ~* '(surf|addison|clarendon|arlene|villa.?vista|1610|morada|medell|escritura|otrosi|alta|closing|deed|wire|master statement|final statement|fidelity|earnest)'

UNION ALL
SELECT 'closing_documents', count(*), 0
FROM (SELECT DISTINCT d.chitty_id
      FROM storage.documents d
      WHERE d.deleted_at IS NULL
        AND d.filename ~* '(alta|closing disclosure|master statement|final statement|warranty deed|settlement statement|otrosi|escritura)') z

UNION ALL
SELECT 'contradictions', count(*), 0 FROM public.contradictions
WHERE contradiction_type IN ('property_purchase_price', 'capital_contribution')

UNION ALL
SELECT 'blockers', count(*), 0 FROM verification.verification_items
WHERE deleted_at IS NULL AND status IN ('pending_review', 'under_review', 'extracted')

UNION ALL
SELECT 'verified_items', count(*), 0 FROM verification.verification_items
WHERE deleted_at IS NULL AND status = 'verified'

ORDER BY 1;

-- ---------------------------------------------------------------------------
-- cc_properties value digest.
--
-- cc_properties contributes no money total, so the aggregate above verifies it
-- by row count only. Its values are nonetheless load-bearing: the generator
-- reads tax_pin, mortgage_servicer and metadata for parcel checks, and
-- metadata.purchase_price feeds a CRITICAL cross-check against the acquisition
-- fact. This digest must equal the "cc_properties value digest" line printed by
-- verify_record_snapshot.py. Field order, the whitespace normalization and the
-- \x1f / \x1e separators are matched to that script deliberately — changing
-- either side alone silently disables the check.

SELECT md5(string_agg(row_digest, E'\x1e' ORDER BY property_name))
       AS cc_properties_value_digest
FROM (
  SELECT property_name,
    concat_ws(E'\x1f',
      btrim(regexp_replace(coalesce(property_name, ''), '\s+', ' ', 'g')),
      btrim(regexp_replace(coalesce(address, ''), '\s+', ' ', 'g')),
      btrim(regexp_replace(coalesce(unit, ''), '\s+', ' ', 'g')),
      btrim(regexp_replace(coalesce(property_type, ''), '\s+', ' ', 'g')),
      btrim(regexp_replace(coalesce(tax_pin, ''), '\s+', ' ', 'g')),
      btrim(regexp_replace(coalesce(mortgage_servicer, ''), '\s+', ' ', 'g')),
      btrim(regexp_replace(coalesce(metadata->>'purchase_date', ''), '\s+', ' ', 'g')),
      btrim(regexp_replace(coalesce(metadata->>'purchase_price', ''), '\s+', ' ', 'g')),
      btrim(regexp_replace(coalesce(metadata->>'municipality', ''), '\s+', ' ', 'g')),
      btrim(regexp_replace(coalesce(metadata->>'state', ''), '\s+', ' ', 'g')),
      btrim(regexp_replace(coalesce(metadata->>'county', ''), '\s+', ' ', 'g')),
      btrim(regexp_replace(coalesce(metadata->>'lender', ''), '\s+', ' ', 'g'))
    ) AS row_digest
  FROM public.cc_properties
) z;
