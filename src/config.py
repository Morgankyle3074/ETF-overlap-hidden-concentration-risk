from pathlib import Path

# Project root = folder that contains data/, notebooks/, src/
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Raw filenames (must match exactly what's in data/raw/)
RAW_FILES = {
    "VOO": "Holdings_details_S&P_500_ETF.csv",
    "SPY": "holdings-daily-us-en-spy.xlsx",
    "QQQ": "QQQ Daily.xlsx",
    "SCHD": "SCHD Daily.xlsx",
}

# Clean outputs
CLEAN_PARQUET = {
    "SPY": "spy_clean.parquet",
    "VOO": "voo_clean.parquet",
    "QQQ": "qqq_clean.parquet",
    "SCHD": "schd_clean.parquet",
}

CLEAN_CSV = {
    "SPY": "spy_clean.csv",
    "VOO": "voo_clean.csv",
    "QQQ": "qqq_clean.csv",
    "SCHD": "schd_clean.csv",
}
