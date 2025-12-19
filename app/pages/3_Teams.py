import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


@st.cache_data
def load_history():
    df = pd.read_csv("data/processed/elo_history.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


st.title("Teams — Elo over time")

hist = load_history()
teams = sorted(set(hist["home_team"]).union(set(hist["away_team"])))
team = st.selectbox("Select team", teams)

st.write("### Recent matches")
recent = hist[(hist["home_team"] == team) | (hist["away_team"] ==
                                             team)].sort_values("date", ascending=False)
st.dataframe(
    recent[["date", "home_team", "away_team", "home_goals", "away_goals"]]
    .reset_index(drop=True)
)
