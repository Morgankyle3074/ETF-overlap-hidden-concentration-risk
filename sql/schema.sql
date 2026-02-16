-- schema.sql

CREATE TABLE IF NOT EXISTS holdings_clean (
  as_of_date DATE,
  etf TEXT NOT NULL,
  holding_name TEXT NOT NULL,
  ticker TEXT,
  weight DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (as_of_date, etf, holding_name)
);

CREATE TABLE IF NOT EXISTS overlap_pairwise (
  as_of_date DATE,
  etf_a TEXT NOT NULL,
  etf_b TEXT NOT NULL,
  overlap_weighted DOUBLE PRECISION NOT NULL,
  overlap_count INTEGER NOT NULL,
  overlap_pct_of_a DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (as_of_date, etf_a, etf_b)
);

CREATE TABLE IF NOT EXISTS concentration_metrics (
  as_of_date DATE,
  entity_type TEXT NOT NULL,   -- 'ETF' or 'PORTFOLIO'
  entity_name TEXT NOT NULL,   -- 'SPY' or 'EQUAL_25_25_25_25'
  hhi DOUBLE PRECISION NOT NULL,
  effective_holdings DOUBLE PRECISION NOT NULL,
  top10_share DOUBLE PRECISION NOT NULL,
  top20_share DOUBLE PRECISION NOT NULL,
  top50_share DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (as_of_date, entity_type, entity_name)
);
