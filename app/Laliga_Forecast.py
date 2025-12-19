import streamlit as st
import pandas as pd


st.set_page_config(page_title="LaLiga Forecast", layout="wide")

_CSS = """
<style>
html, body {background-color: #0f1724;}
.stApp { color-scheme: light; }
.hero {background: linear-gradient(90deg,#0f1724 0%, #0b3d91 100%); padding: 28px; border-radius: 8px;}
.card {background: #ffffff11; padding: 16px; border-radius: 8px;}
.muted {color: #cbd5e1}
</style>
"""

st.markdown(_CSS, unsafe_allow_html=True)

with st.container():
    cols = st.columns([1, 3])

    with cols[1]:
        st.markdown("""
		<div class="hero">
		<h1 style='color: #fff; margin: 0;'>LaLiga Match Analysis + Predictions</h1>
		<p class='muted'>Interactive Elo-based match probability visualiser with backtests and team histories.</p>
		</div>
		""", unsafe_allow_html=True)


try:
    latest = pd.read_csv("data/processed/latest_ratings.csv")
    st.sidebar.write("### Top teams")
    st.sidebar.table(latest.head(6).set_index("team"))
except Exception:
    st.sidebar.info("Run the pipeline to populate `latest_ratings.csv`.")
