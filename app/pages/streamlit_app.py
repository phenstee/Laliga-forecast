import streamlit as st

st.sidebar.title("Navigation")
st.sidebar.write("Use the page list above to switch pages.")

st.set_page_config(page_title="LaLiga Forecast", layout="wide")

st.title("LaLiga Match Analysis + Forecast")
st.write("""
This app loads cleaned match data, computes Elo ratings, and shows match win/draw/loss probabilities.

**Run pipeline first:**
1) `python src/clean_data.py`
2) `python src/elo.py`
3) `python src/backtest.py`
""")
st.info("Use the sidebar pages to view Fixtures, Match Preview, Teams, and Backtest.")
