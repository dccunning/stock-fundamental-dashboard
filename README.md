## Stock Fundamental Dashboard

Visualize and identify undervalued stocks using valuation ratios and trends from SEC filings.


## Features

- Load yearly financial data from local CSVs or a database
- Explore fundamentals and custom valuation metrics in an interactive, color-coded dashboard
- View bar charts of specific metrics over time for any stock
- View charts of a stock with the TradingView integration


## Project Structure

```
app/                  # Logic for views like YOY breakdowns
data/                 # Static data files and config
    └── sec_cleaned/  # Cleaned SEC financials to be accesed by
sec_scraper/          # Raw SEC data collection and data cleaning logic
streamlit_dashboard/  # Reusable dashboard components (UI, helpers, constants)
main.py               # Streamlit app entry point
```

## Start Dashboard

1. Update CIK-tickers data. Run: 
```
sec_scraper/cik_tickers.py
```

2. Update SEC financials. Run:
```
sec_scraper/sec_financials.py
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Run:
```
streamlit run main.py
```

## Dev Work To Do
1. Create a tab for viewing and adding stocks to the universe of stocks
2. Setup the database connection