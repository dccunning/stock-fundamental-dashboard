import os
from typing import List
from sec_scraper.cik_tickers import load_ticker_mapping
from secfsdstools.e_collector.companycollecting import CompanyReportCollector
from secfsdstools.e_filter.rawfiltering import (
    ReportPeriodRawFilter, MainCoregRawFilter,
    OfficialTagsOnlyRawFilter, USDOnlyRawFilter
)
from secfsdstools.f_standardize.cf_standardize import CashFlowStandardizer
from secfsdstools.f_standardize.bs_standardize import BalanceSheetStandardizer
from secfsdstools.f_standardize.is_standardize import IncomeStatementStandardizer


parent_dir = os.path.dirname(os.getcwd())
SEC_DATA_FOLDER = os.path.join(parent_dir, "data/sec_cleaned/")


def _get_standardized_statements(joined_bag):
    """
    Apply standardisers and filter for annual 10-K reports

    :param joined_bag: Joined raw data bag from SEC reports
    :return: (cf_df, bs_df, is_df) filtered dataframes
    """
    cf = CashFlowStandardizer()
    bs = BalanceSheetStandardizer()
    is_ = IncomeStatementStandardizer()

    cf_df = joined_bag.present(cf)
    cf_df = cf_df[(cf_df.fp == "FY") & (cf_df.qtrs == 4) & (cf_df.form == "10-K")].copy()

    bs_df = joined_bag.present(bs)
    bs_df = bs_df[(bs_df.fp == "FY") & (bs_df.form == "10-K")].copy()

    is_df = joined_bag.present(is_)
    is_df = is_df[(is_df.fp == "FY") & (is_df.qtrs == 4) & (is_df.form == "10-K")].copy()

    return cf_df, bs_df, is_df


def _align_and_validate_years(cf_df, bs_df, is_df):
    """
    Align and validate fiscal years across financial statements.

    :param cf_df: Cash Flow DataFrame
    :param bs_df: Balance Sheet DataFrame
    :param is_df: Income Statement DataFrame
    :return: Aligned and trimmed (cf_df, bs_df, is_df)
    :raises ValueError: If fiscal years do not match across statements
    """
    common_years = set(cf_df['fy']) & set(bs_df['fy']) & set(is_df['fy'])

    cf_df = cf_df[cf_df['fy'].isin(common_years)].sort_values('fy', ascending=False).reset_index(drop=True)
    bs_df = bs_df[bs_df['fy'].isin(common_years)].sort_values('fy', ascending=False).reset_index(drop=True)
    is_df = is_df[is_df['fy'].isin(common_years)].sort_values('fy', ascending=False).reset_index(drop=True)

    min_rows = min(len(cf_df), len(bs_df), len(is_df))
    cf_df, bs_df, is_df = cf_df.head(min_rows), bs_df.head(min_rows), is_df.head(min_rows)

    if not (cf_df['fy'].equals(bs_df['fy']) and cf_df['fy'].equals(is_df['fy'])):
        raise ValueError("Mismatch in fiscal years across financial statements")

    return cf_df, bs_df, is_df


def fetch_sec_financials(cik: int):
    """
    Fetch standardized annual 10-K financials for a given CIK.

    :param cik: Central Index Key for the company
    :return: Tuple of (cf_df, bs_df, is_df) DataFrames
    """
    collector = CompanyReportCollector.get_company_collector(ciks=[cik])
    raw_data = collector.collect()

    filtered = raw_data[ReportPeriodRawFilter()][MainCoregRawFilter()][OfficialTagsOnlyRawFilter()][USDOnlyRawFilter()]
    joined = filtered.join()

    cf_df, bs_df, is_df = _get_standardized_statements(joined)
    return _align_and_validate_years(cf_df, bs_df, is_df)


def save_sec_financials(exchange_ticker: str, cik: int):
    """
    Save SEC financials for a given ticker and CIK.

    :param exchange_ticker: Ticker in EXCHANGE:TICKER format
    :param cik: Central Index Key
    """
    cf_df, bs_df, is_df = fetch_sec_financials(cik)
    merged = (
        cf_df
        .merge(bs_df, on=["cik", "name", "form", "fye", "ddate"], how='outer')
        .merge(is_df, on=["cik", "name", "form", "fye", "ddate"], how='outer')
    )

    exchange, ticker = exchange_ticker.split(':')

    merged.to_csv(f"{SEC_DATA_FOLDER}{exchange}__{ticker}.csv", index=False)


def save_all_ticker_data(tickers: List[str]):
    """
    Save SEC financial data for a list of exchange tickers.

    :param tickers: List of 'EXCHANGE:TICKER' strings
    """
    cik_mapping = load_ticker_mapping()
    for ticker in tickers:
        try:
            save_sec_financials(exchange_ticker=ticker, cik=cik_mapping.get(ticker))
            print('Done:', ticker)
        except Exception as e:
            print('Failed:', ticker, str(e))


if __name__ == "__main__":
    from sec_scraper.universe import UNIVERSE
    save_all_ticker_data(UNIVERSE)
