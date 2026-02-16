from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd

from .config import RAW_DIR, RAW_FILES, PROCESSED_DIR


def read_csv_safe(path: Path) -> pd.DataFrame:
    """Read CSV with common encodings."""
    last_err = None
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin1"):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception as e:
            last_err = e
            continue
    raise ValueError(f"Could not read CSV: {path}\nLast error: {last_err}")


def read_excel_safe(path: Path, sheet_name=0) -> pd.DataFrame:
    """Read Excel. Defaults to first sheet."""
    return pd.read_excel(path, sheet_name=sheet_name)


def assert_raw_files_exist(raw_dir: Path = RAW_DIR) -> Dict[str, Path]:
    """Return dict of ETF -> full path, or raise if any missing."""
    paths = {k: raw_dir / fname for k, fname in RAW_FILES.items()}
    missing = [k for k, p in paths.items() if not p.exists()]
    if missing:
        found = sorted([p.name for p in raw_dir.glob("*")])
        raise FileNotFoundError(
            f"Missing raw files for: {missing}\n"
            f"Expected names: {list(RAW_FILES.values())}\n"
            f"Found in raw/: {found}"
        )
    return paths


@dataclass
class RawHoldings:
    voo_raw: pd.DataFrame
    spy_raw: pd.DataFrame
    qqq_raw: pd.DataFrame
    schd_raw: pd.DataFrame


def load_raw_holdings(raw_dir: Path = RAW_DIR) -> RawHoldings:
    """Load all raw holdings files into dataframes."""
    paths = assert_raw_files_exist(raw_dir)

    voo_raw = read_csv_safe(paths["VOO"])
    spy_raw = read_excel_safe(paths["SPY"])
    qqq_raw = read_excel_safe(paths["QQQ"])
    schd_raw = read_excel_safe(paths["SCHD"])

    return RawHoldings(
        voo_raw=voo_raw,
        spy_raw=spy_raw,
        qqq_raw=qqq_raw,
        schd_raw=schd_raw,
    )


def quick_profile(df: pd.DataFrame, name: str, head_n: int = 8) -> Dict:
    """Lightweight dataframe profiling (returns a dict, prints optional)."""
    profile = {
        "name": name,
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).value_counts().to_dict(),
        "missing_pct_top15": (df.isna().mean().sort_values(ascending=False).head(15) * 100).round(2).to_dict(),
        "head": df.head(head_n),
    }
    return profile


def ensure_processed_dir(processed_dir: Path = PROCESSED_DIR) -> None:
    processed_dir.mkdir(parents=True, exist_ok=True)

