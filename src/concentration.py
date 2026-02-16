from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd


def hhi(weights: pd.Series) -> float:
    """HHI = sum(w^2). Weights should be decimals summing ~1."""
    w = pd.to_numeric(weights, errors="coerce").fillna(0.0)
    return float((w ** 2).sum())


def effective_holdings(weights: pd.Series) -> float:
    """Effective holdings = 1 / HHI."""
    h = hhi(weights)
    return float(1.0 / h) if h > 0 else float("nan")


def topn_share(weights: pd.Series, n: int) -> float:
    """Share of portfolio in top n holdings (decimal)."""
    w = pd.to_numeric(weights, errors="coerce").dropna()
    return float(w.sort_values(ascending=False).head(n).sum())


@dataclass
class ConcentrationSummary:
    hhi: float
    effective_holdings: float
    top10_share: float
    top20_share: float
    top50_share: float


def summarize_concentration(weights: pd.Series) -> ConcentrationSummary:
    return ConcentrationSummary(
        hhi=hhi(weights),
        effective_holdings=effective_holdings(weights),
        top10_share=topn_share(weights, 10),
        top20_share=topn_share(weights, 20),
        top50_share=topn_share(weights, 50),
    )


def etf_concentration_metrics(df: pd.DataFrame) -> ConcentrationSummary:
    """
    df must have a 'weight' column (decimal weights).
    """
    return summarize_concentration(df["weight"])


def portfolio_concentration_metrics(portfolio_weights: pd.Series) -> ConcentrationSummary:
    """
    portfolio_weights: Series indexed by holding_name with decimal weights.
    """
    return summarize_concentration(portfolio_weights)
