import os
import pandas as pd
from app.yoy_financials import stock_yoy_financials

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOCK_DIR = os.path.join(BASE_DIR, 'data/sec_cleaned')


def fetch_yoy_data(symbol: str) -> pd.DataFrame:
    """
    Reads raw CSV for `symbol`, runs stock_yoy_financials,
    returns a DataFrame: rows=metrics, cols=years
    """
    exchange, ticker = symbol.split(":")
    path = os.path.join(STOCK_DIR, f"{exchange}__{ticker}.csv")
    raw = pd.read_csv(path)
    return stock_yoy_financials(raw)


def format_cell(val):
    """Format cell value to suppress trailing zeroes (general format)."""
    if pd.isna(val) or val == "":
        return ""
    try:
        return format(float(val), "g")
    except Exception:
        return val


def highlight_outliers(row: pd.Series) -> list[str]:
    """
    For each row (metric), highlight max (green) and min (red) cells.
    """
    num = pd.to_numeric(row, errors='coerce')
    if num.notna().sum() == 0:
        return [""] * len(row)

    mx, mn = num.max(), num.min()
    styles = []
    for v in row:
        try:
            f = float(v)
        except Exception:
            styles.append("")
            continue
        if f == mx:
            styles.append("background-color: rgba(0, 255, 0, 0.1)")
        elif f == mn:
            styles.append("background-color: rgba(255, 0, 0, 0.1)")
        else:
            styles.append("")
    return styles
