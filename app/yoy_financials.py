from pandas import DataFrame
import pandas as pd

MILLIONS = 1_000_000


def _preprocess(merged):
    """Add 'Year' and 'PeriodEnd', filter to annual, drop duplicates."""
    merged['Year'] = merged['ddate'].astype(str).str[:4].astype('Int64')
    merged['PeriodEnd'] = pd.to_datetime(merged['date'], errors='coerce').dt.strftime('%m-%d')
    annual = merged[merged['fp'] == 'FY']
    return annual.drop_duplicates(subset=['Year']).sort_values('Year')


def _scale_and_rolling(annual):
    """Add scaled and 3-year rolling metrics."""
    annual['Revenues '] = (annual['Revenues'] / MILLIONS).round(0).astype('Int64')
    annual['Assets '] = (annual['Assets'] / MILLIONS).round(0).astype('Int64')
    annual['Revs Avg3'] = annual['Revenues '].rolling(3, min_periods=3).mean().round(0).astype('Int64')
    annual['Outstanding Sh '] = (annual['OutstandingShares'] / MILLIONS).round(0).astype('Int64')
    return annual


def _add_ratios(annual):
    """Add financial ratios."""
    def _denominator():
        return (annual['Assets'] - (
            annual['LiabilitiesCurrent'] + annual['LiabilitiesNoncurrent']
            - (annual['ProceedsFromIssuanceOfDebt'].fillna(0) - annual['RepaymentsOfDebt'].fillna(0))
        )).replace(0, pd.NA)

    d = _denominator()

    annual['AssetTurnover'] = annual['Revenues'] / annual['Assets']
    annual['Turnover Avg3'] = annual['AssetTurnover'].rolling(3, min_periods=3).mean().round(2)

    annual['Gross Profit / TOA'] = annual['GrossProfit'] / d
    annual['Gross Profit / TOA Avg3'] = annual['Gross Profit / TOA'].rolling(3, min_periods=3).mean().round(2)

    annual['EBIT_adj / TOA'] = (
        (annual['OperatingIncomeLoss'] + annual['DepreciationDepletionAndAmortization'].fillna(0)) / d
    )
    annual['EBIT adj / TOA Avg3'] = annual['EBIT_adj / TOA'].rolling(3, min_periods=3).mean().round(2)

    annual['ROIC'] = (
        (annual['IncomeLossFromContinuingOperationsBeforeIncomeTaxExpenseBenefit'] -
         annual['AllIncomeTaxExpenseBenefit']) / d
    )
    annual['ROIC Avg3'] = annual['ROIC'].rolling(3, min_periods=3).mean().round(2)

    annual['CROSIC'] = annual['NetCashProvidedByUsedInOperatingActivities'] / d
    annual['CROSIC Avg3'] = annual['CROSIC'].rolling(3, min_periods=3).mean().round(2)

    annual['GrossMargin'] = annual['GrossProfit'] / annual['Revenues']
    annual['GrossMargin Avg3'] = annual['GrossMargin'].rolling(3, min_periods=3).mean().round(2)

    annual['EBITDA Margin Avg3'] = (
        (annual['OperatingIncomeLoss'] + annual['DepreciationDepletionAndAmortization'].fillna(0))
        / annual['Revenues'].replace(0, pd.NA)
    ).rolling(3, min_periods=3).mean().round(2)

    annual['Net Inc Margin Avg3'] = (
        annual['NetIncomeLoss'].fillna(0) / annual['Revenues'].replace(0, pd.NA)
    ).rolling(3, min_periods=3).mean().round(2)

    annual['CFO Margin Avg3'] = (
        annual['NetCashProvidedByUsedInOperatingActivities'].fillna(0)
        / annual['Revenues'].replace(0, pd.NA)
    ).rolling(3, min_periods=3).mean().round(2)

    annual['SFCF Margin Avg3'] = (
        (annual['NetCashProvidedByUsedInOperatingActivities'] -
         annual['PaymentsToAcquirePropertyPlantAndEquipment'])
        / annual['Revenues'].replace(0, pd.NA)
    ).rolling(3, min_periods=3).mean().round(2)

    annual['NCF Margin Avg3'] = (
        annual['CashPeriodIncreaseDecreaseIncludingExRateEffectFinal'].fillna(0)
        / annual['Revenues'].replace(0, pd.NA)
    ).rolling(3, min_periods=3).mean().round(2)

    return annual


def _per_share_metrics(annual):
    """Add per-share metrics."""
    shares = annual['OutstandingShares'].replace(0, pd.NA)

    annual['Revs/sh'] = (annual['Revenues'].fillna(0) / shares).round(2)
    annual['Assets/sh'] = (annual['Assets'].fillna(0) / shares).round(2)
    annual['Book/sh'] = (annual['Equity'].fillna(0) / shares).round(2)
    annual['Net Excess Cash/sh'] = (annual['CashAndCashEquivalentsEndOfPeriod'].fillna(0) / shares).round(2)
    annual['Div/sh'] = (annual['PaymentsOfDividends'].fillna(0) / shares).round(2)

    annual['ROE 3yr%'] = (
        (annual['NetIncomeLoss'].fillna(0) / annual['Equity'].replace(0, pd.NA))
        .rolling(3, min_periods=3).mean().round(2)
    )
    annual['ROE 5yr%'] = (
        (annual['NetIncomeLoss'].fillna(0) / annual['Equity'].replace(0, pd.NA))
        .rolling(5, min_periods=5).mean().round(2)
    )

    return annual


def stock_yoy_financials(stock_data: DataFrame) -> DataFrame:
    """
    Generate YoY financials of financial metrics for a given stock.

    :param stock_data: Combined financial statement data
    :return: Metrics by year and period end
    """
    annual = _preprocess(stock_data)
    annual = _scale_and_rolling(annual)
    annual = _add_ratios(annual)
    annual = _per_share_metrics(annual)

    return annual.set_index(['Year', 'PeriodEnd']).transpose()
