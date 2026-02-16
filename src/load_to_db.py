from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict

import pandas as pd
import numpy as np

from .overlap import run_overlap, to_long_matrix, build_portfolio_weights
from .concentration import summarize_concentration


def connect_sqlite(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def write_df(conn: sqlite3.Connection, df: pd.DataFrame, table: str, if_exists: str = "replace") -> None:
    df.to_sql(table, conn, if_exists=if_exists, index=False)


def build_holdings_clean_table(spy: pd.DataFrame, voo: pd.DataFrame, qqq: pd.DataFrame, schd: pd.DataFrame) -> pd.DataFrame:
    """
    Expect each df has: etf, holding_name, ticker, weight
    Returns combined holdings table (no as_of_date by default).
    """
    return pd.concat([spy, voo, qqq, schd], ignore_index=True)


def export_tableau_extracts(
    out_dir: Path,
    holdings_clean: pd.DataFrame,
    portfolio: Dict[str, float] | None = None,
) -> Dict[str, Path]:
    """
    Writes CSVs designed for Tableau Public manual upload.
    Returns dict of written file paths.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    written: Dict[str, Path] = {}

    # Base holdings
    p = out_dir / "holdings_clean_long.csv"
    holdings_clean.to_csv(p, index=False)
    written["holdings_clean_long"] = p

    # Overlap outputs
    overlap = run_overlap(holdings_clean)

    p = out_dir / "overlap_weighted_long.csv"
    to_long_matrix(overlap.weighted_overlap, "overlap_weighted").to_csv(p, index=False)
    written["overlap_weighted_long"] = p

    p = out_dir / "overlap_count_long.csv"
    to_long_matrix(overlap.overlap_count, "overlap_count").to_csv(p, index=False)
    written["overlap_count_long"] = p

    p = out_dir / "overlap_pct_long.csv"
    to_long_matrix(overlap.overlap_pct, "overlap_pct_of_a").to_csv(p, index=False)
    written["overlap_pct_long"] = p

    # ETF concentration metrics
    rows = []
    for etf in ["SPY", "VOO", "QQQ", "SCHD"]:
        w = holdings_clean.loc[holdings_clean["etf"].str.upper() == etf, "weight"]
        s = summarize_concentration(w)
        rows.append({
            "entity_type": "ETF",
            "entity_name": etf,
            "hhi": s.hhi,
            "effective_holdings": s.effective_holdings,
            "top10_share": s.top10_share,
            "top20_share": s.top20_share,
            "top50_share": s.top50_share,
        })

    # Portfolio metrics + portfolio holdings if provided
    if portfolio is not None:
        W = overlap.W
        port = build_portfolio_weights(W, portfolio)

        s = summarize_concentration(port)
        rows.append({
            "entity_type": "PORTFOLIO",
            "entity_name": "CUSTOM_PORTFOLIO",
            "hhi": s.hhi,
            "effective_holdings": s.effective_holdings,
            "top10_share": s.top10_share,
            "top20_share": s.top20_share,
            "top50_share": s.top50_share,
        })

        p = out_dir / "portfolio_holdings_top200.csv"
        port.head(200).reset_index().rename(columns={"index": "holding_name", 0: "portfolio_weight"}).to_csv(p, index=False)
        written["portfolio_holdings_top200"] = p

    p = out_dir / "concentration_metrics.csv"
    pd.DataFrame(rows).to_csv(p, index=False)
    written["concentration_metrics"] = p

    return written
