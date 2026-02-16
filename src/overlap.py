from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd


@dataclass
class OverlapResults:
    W: pd.DataFrame                   # holding_name x etf weight matrix
    overlap_count: pd.DataFrame       # etf x etf shared holding counts
    overlap_pct: pd.DataFrame         # etf x etf % of A holdings also in B (count-based)
    weighted_overlap: pd.DataFrame    # etf x etf sum(min(wA,wB))


def build_weight_matrix(holdings: pd.DataFrame) -> pd.DataFrame:
    """
    holdings columns required: holding_name, etf, weight
    Returns W: index=holding_name, columns=etf, values=weight, fill=0
    """
    df = holdings.copy()
    df["holding_name"] = df["holding_name"].astype(str).str.strip().str.upper()
    df["etf"] = df["etf"].astype(str).str.strip().str.upper()

    W = df.pivot_table(
        index="holding_name",
        columns="etf",
        values="weight",
        aggfunc="sum",
        fill_value=0.0,
    )
    return W


def overlap_count_matrix(W: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns:
      overlap_count: etf x etf shared holding counts
      overlap_pct: etf x etf % of A holdings that are also in B (count-based)
    """
    present = (W > 0).astype(int)
    etfs = list(W.columns)

    overlap_count = present.T @ present
    holding_counts = present.sum(axis=0)  # per ETF

    overlap_pct = overlap_count.copy().astype(float)
    for a in etfs:
        overlap_pct.loc[a, :] = overlap_pct.loc[a, :] / float(holding_counts[a])

    return overlap_count, overlap_pct


def weighted_overlap_matrix(W: pd.DataFrame) -> pd.DataFrame:
    """
    weighted_overlap(A,B) = sum_i min(w_iA, w_iB)
    Returns etf x etf matrix.
    """
    etfs = list(W.columns)
    out = pd.DataFrame(index=etfs, columns=etfs, dtype=float)

    for a in etfs:
        for b in etfs:
            out.loc[a, b] = np.minimum(W[a], W[b]).sum()

    return out


def top_overlap(W: pd.DataFrame, a: str, b: str, n: int = 15) -> pd.DataFrame:
    """
    Return top overlapping holdings between two ETFs by overlap contribution.
    Requires W built with holding_name index and ETF columns.
    """
    a = a.strip().upper()
    b = b.strip().upper()

    df = pd.DataFrame({
        "holding_name": W.index,
        f"w_{a}": W[a].values,
        f"w_{b}": W[b].values,
    })
    df["overlap_contrib"] = np.minimum(df[f"w_{a}"], df[f"w_{b}"])
    df = df[df["overlap_contrib"] > 0].sort_values("overlap_contrib", ascending=False)
    return df.head(n).reset_index(drop=True)


def build_portfolio_weights(W: pd.DataFrame, portfolio: Dict[str, float]) -> pd.Series:
    """
    portfolio: dict ETF -> weight (must sum to ~1)
    Returns Series indexed by holding_name with portfolio holding weights.
    """
    port = pd.Series(0.0, index=W.index)
    for etf, w in portfolio.items():
        etf_u = etf.strip().upper()
        port += float(w) * W[etf_u]
    return port.sort_values(ascending=False)


def run_overlap(holdings: pd.DataFrame) -> OverlapResults:
    """
    Convenience function to run all overlap outputs from a holdings dataframe.
    """
    W = build_weight_matrix(holdings)
    overlap_count, overlap_pct = overlap_count_matrix(W)
    weighted_overlap = weighted_overlap_matrix(W)
    return OverlapResults(W=W, overlap_count=overlap_count, overlap_pct=overlap_pct, weighted_overlap=weighted_overlap)


def to_long_matrix(mat: pd.DataFrame, value_name: str) -> pd.DataFrame:
    """
    Convert an etf x etf matrix to long format for Tableau:
    columns: etf_a, etf_b, <value_name>
    """
    long = mat.copy()
    long.index.name = "etf_a"
    long = long.reset_index().melt(id_vars="etf_a", var_name="etf_b", value_name=value_name)
    return long
