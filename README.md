## Stock Fundamental Dashboard

Visualize and identify undervalued stocks using valuation ratios and trends from SEC filings.


## Features

- Load yearly financial data from local CSVs or a database
- Explore fundamentals and custom valuation metrics in an interactive, color-coded dashboard
- View bar charts of specific metrics over time for any stock
- View charts of a stock with the TradingView integration


## Tab Screenshots

<img width="671" height="420" alt="Screenshot 2025-07-24 at 8 23 45 AM" src="https://github.com/user-attachments/assets/35fbfc1c-0b29-42ee-aa73-25105d9df1ab" />
<img width="671" height="420" alt="Screenshot 2025-07-24 at 8 24 06 AM" src="https://github.com/user-attachments/assets/b683c730-f367-4812-8a0a-d143a76f953a" />
<img width="671" height="429" alt="Screenshot 2025-07-24 at 8 24 25 AM" src="https://github.com/user-attachments/assets/9c680d4d-c7c0-4f7d-94af-aad1f11367c7" />


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
