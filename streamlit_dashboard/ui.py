import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
from streamlit_dashboard.helpers import fetch_yoy_data, format_cell, highlight_outliers
from streamlit_dashboard.constants import YOY_DESCRIPTIONS
from sec_scraper.universe import UNIVERSE


def show_yoy_financials_tab():
    """
    Display a styled year-over-year financial table for a selected symbol.

    Allows users to select a symbol from the universe and view its
    financial metrics in a formatted dataframe with outlier highlights.
    """
    st.header("Year-over-Year Financials")

    symbol = st.selectbox("Select symbol", UNIVERSE)
    df = fetch_yoy_data(symbol)
    df = df[df.index.isin(YOY_DESCRIPTIONS.keys())]
    df.columns.names = ["Year", "Period End"]

    df_display = df.copy().reset_index()
    df_display = df_display.rename(columns={"index": "Metrics"})

    styled = (
        df_display
        .style
        .format(format_cell)
        .apply(highlight_outliers, axis=1)
    )

    st.write(f"## {symbol}")
    st.dataframe(styled, use_container_width=True, height=700)


def show_live_chart_tab():
    """
    Embed a live TradingView chart for the selected symbol.
    Uses TradingView's chart widget and tools for technical analysis.
    """
    st.header("Live Chart")
    symbol = st.selectbox("Choose symbol to view chart", UNIVERSE, key="chart_select")

    tv_widget_html = f"""
    <div id='tv_chart_container' style='width:100%;height:700px;'></div>
    <script type='text/javascript' src='https://s3.tradingview.com/tv.js'></script>
    <script type='text/javascript'>
      new TradingView.widget({{
        container_id: "tv_chart_container",
        symbol: "{symbol}",
        interval: "D",
        autosize: true,
        theme: "dark",
        style: "1",
        hide_side_toolbar: false,
        withdateranges: true,
        allow_symbol_change: true,
        studies: [
          {{ id: "MASimple@tv-basicstudies", inputs: {{ length: 50 }} }},
          {{ id: "MASimple@tv-basicstudies", inputs: {{ length: 200 }} }}
        ],
        support_host: "https://www.tradingview.com"
      }});
    </script>
    """
    components.html(tv_widget_html, height=800, scrolling=False)


def show_financial_bar_chart():
    """
    Render a bar chart of a selected financial metric over time.

    Lets the user pick a symbol and metric, and visualizes its yearly trend.
    """
    st.header("Financial Bar Charts")

    symbol = st.selectbox("Select symbol", UNIVERSE, key="bar_symbol")

    metric = st.selectbox(
        "Select metric",
        list(YOY_DESCRIPTIONS.keys()),
        format_func=lambda x: f"{x} — {YOY_DESCRIPTIONS[x][0]}",
        key="bar_metric"
    )

    df = fetch_yoy_data(symbol)

    if metric not in df.index:
        st.warning(f"Metric '{metric}' not available for {symbol}")
        return

    series = df.loc[metric].fillna(0).astype(float)
    years = series.index.get_level_values("Year").astype(str)
    values = series.values

    ylabel = YOY_DESCRIPTIONS[metric][1]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(years, values, color="skyblue")
    ax.set_title(f"{metric} for {symbol}", fontsize=10)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Year")
    ax.tick_params(axis='x', rotation=45)
    fig.tight_layout()

    # Show chart in centered column
    left, center, right = st.columns([1, 3, 1])
    with center:
        st.pyplot(fig)
