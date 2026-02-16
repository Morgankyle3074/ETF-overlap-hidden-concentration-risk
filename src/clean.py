from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import re

from .config import PROCESSED_DIR, CLEAN_PARQUET, CLEAN_CSV


def clean_text(x):
    if pd.isna(x):
        return np.nan
    s = str(x).strip()
    s = re.sub(r"\s+", " ", s)
    return s


def to_decimal_weight(series: pd.Series) -> pd.Series:
    """
    Convert weights to decimal fractions.
    Handles:
      - "7.83%" -> 0.0783
      - "0.0783" -> 0.0783
      - 7.83 (percent units) -> 0.0783 (if median > 1)
      - 0.0472 -> 0.0472
    """
    s = series.copy()
    s_str = s.astype(str)

    has_pct = s_str.str.contains("%", na=False)

    out = pd.to_numeric(
        s_str.str.replace("%", "", regex=False).str.replace(",", "", regex=False),
        errors="coerce",
    )

    # Convert percent-signed rows
    out.loc[has_pct] = out.loc[has_pct] / 100.0

    # If overall looks like percent scale, divide by 100
    med = np.nanmedian(out.values)
    if med > 1:
        out = out / 100.0

    return out


def standard_schema(df: pd.DataFrame, etf: str) -> pd.DataFrame:
    out = df.copy()
    out["etf"] = etf
    return out[["etf", "holding_name", "ticker", "weight"]]


# -------- ETF-specific cleaners --------

def clean_spy(spy_raw: pd.DataFrame) -> pd.DataFrame:
    """
    SPY sheet has metadata rows; actual header lives at row index 3.
    Weight is in percent units (e.g., 7.77 for 7.77%).
    """
    spy = spy_raw.copy()

    # Repair header
    spy.columns = spy.iloc[3].astype(str)
    spy = spy.iloc[4:].reset_index(drop=True)

    spy = spy.rename(columns={"Name": "holding_name", "Ticker": "ticker", "Weight": "weight"})
    spy = spy[["holding_name", "ticker", "weight"]]

    spy["holding_name"] = spy["holding_name"].map(clean_text).str.upper()
    spy["ticker"] = spy["ticker"].map(clean_text).str.upper()

    # Force numeric then convert percent -> decimal
    spy["weight"] = pd.to_numeric(spy["weight"], errors="coerce") / 100.0

    spy = spy.dropna(subset=["holding_name", "ticker", "weight"])
    spy = spy[spy["weight"] > 0]

    return standard_schema(spy, "SPY")


def clean_voo(voo_raw: pd.DataFrame) -> pd.DataFrame:
    voo = voo_raw.copy()

    voo = voo.rename(columns={"HOLDINGS": "holding_name", "TICKER": "ticker", "% OF FUNDS*": "weight"})
    voo = voo[["holding_name", "ticker", "weight"]]

    voo["holding_name"] = voo["holding_name"].map(clean_text).str.upper()
    voo["ticker"] = voo["ticker"].map(clean_text).str.upper()
    voo["weight"] = to_decimal_weight(voo["weight"])

    # Drop footer/blank rows
    voo = voo.dropna(subset=["holding_name", "ticker", "weight"])
    voo = voo[voo["weight"] > 0]

    return standard_schema(voo, "VOO")


def clean_qqq(qqq_raw: pd.DataFrame) -> pd.DataFrame:
    qqq = qqq_raw.copy()

    qqq = qqq.rename(columns={"Company": "holding_name", "Allocation": "weight"})
    qqq["ticker"] = np.nan  # file doesn't include tickers

    qqq = qqq[["holding_name", "ticker", "weight"]]
    qqq["holding_name"] = qqq["holding_name"].map(clean_text).str.upper()
    qqq["weight"] = to_decimal_weight(qqq["weight"])

    qqq = qqq.dropna(subset=["holding_name", "weight"])
    qqq = qqq[qqq["weight"] > 0]

    return standard_schema(qqq, "QQQ")


def clean_schd(schd_raw: pd.DataFrame) -> pd.DataFrame:
    schd = schd_raw.copy()

    schd = schd.rename(columns={"Fund Name": "holding_name", "Symbol": "ticker", "% of Assets": "weight"})
    schd = schd[["holding_name", "ticker", "weight"]]

    schd["holding_name"] = schd["holding_name"].map(clean_text).str.upper()
    schd["ticker"] = schd["ticker"].map(clean_text).str.upper()
    schd["weight"] = pd.to_numeric(schd["weight"], errors="coerce")

    schd = schd.dropna(subset=["holding_name", "ticker", "weight"])
    schd = schd[schd["weight"] > 0]

    return standard_schema(schd, "SCHD")


# -------- Orchestration / validation / saving --------

@dataclass
class CleanHoldings:
    spy_clean: pd.DataFrame
    voo_clean: pd.DataFrame
    qqq_clean: pd.DataFrame
    schd_clean: pd.DataFrame


def clean_all(voo_raw: pd.DataFrame, spy_raw: pd.DataFrame, qqq_raw: pd.DataFrame, schd_raw: pd.DataFrame) -> CleanHoldings:
    return CleanHoldings(
        spy_clean=clean_spy(spy_raw),
        voo_clean=clean_voo(voo_raw),
        qqq_clean=clean_qqq(qqq_raw),
        schd_clean=clean_schd(schd_raw),
    )


def validate(df: pd.DataFrame, label: str) -> Dict:
    out = {
        "label": label,
        "rows": int(len(df)),
        "weight_sum": float(df["weight"].sum()),
        "min_weight": float(df["weight"].min()),
        "max_weight": float(df["weight"].max()),
        "missing_ticker_pct": float(df["ticker"].isna().mean() * 100),
    }
    return out


def save_clean_outputs(clean: CleanHoldings, processed_dir: Path = PROCESSED_DIR, parquet: bool = True, csv: bool = True) -> Dict[str, Path]:
    processed_dir.mkdir(parents=True, exist_ok=True)
    written: Dict[str, Path] = {}

    mapping = {
        "SPY": clean.spy_clean,
        "VOO": clean.voo_clean,
        "QQQ": clean.qqq_clean,
        "SCHD": clean.schd_clean,
    }

    for etf, df in mapping.items():
        if parquet:
            p = processed_dir / CLEAN_PARQUET[etf]
            df.to_parquet(p, index=False, engine="pyarrow")
            written[f"{etf}_parquet"] = p
        if csv:
            c = processed_dir / CLEAN_CSV[etf]
            df.to_csv(c, index=False)
            written[f"{etf}_csv"] = c

    return written
