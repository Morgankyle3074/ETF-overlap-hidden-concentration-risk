-- views.sql

-- A clean view for Tableau
CREATE VIEW IF NOT EXISTS v_holdings_clean AS
SELECT
  as_of_date,
  etf,
  holding_name,
  ticker,
  weight,
  weight * 100.0 AS weight_pct
FROM holdings_clean;

-- Pairwise overlap matrix view
CREATE VIEW IF NOT EXISTS v_overlap_matrix AS
SELECT
  as_of_date,
  etf_a,
  etf_b,
  overlap_weighted,
  overlap_weighted * 100.0 AS overlap_weighted_pct,
  overlap_count,
  overlap_pct_of_a
FROM overlap_pairwise;

-- Concentration metrics view
CREATE VIEW IF NOT EXISTS v_concentration AS
SELECT
  as_of_date,
  entity_type,
  entity_name,
  hhi,
  effective_holdings,
  top10_share * 100.0 AS top10_pct,
  top20_share * 100.0 AS top20_pct,
  top50_share * 100.0 AS top50_pct
FROM concentration_metrics;
