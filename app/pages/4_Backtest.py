import streamlit as st
import pandas as pd
import numpy as np


@st.cache_data
def load_hist():
    df = pd.read_csv("data/processed/elo_history.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


def actual_outcome(row):
    if row["home_goals"] > row["away_goals"]:
        return "H"
    if row["home_goals"] < row["away_goals"]:
        return "A"
    return "D"


st.title("Backtest")

df = load_hist()
eps = 1e-12
df["p_home"] = df["p_home"].clip(eps, 1-eps)
df["p_draw"] = df["p_draw"].clip(eps, 1-eps)
df["p_away"] = df["p_away"].clip(eps, 1-eps)

df["actual"] = df.apply(actual_outcome, axis=1)
df["pred"] = df[["p_home", "p_draw", "p_away"]].idxmax(
    axis=1).map({"p_home": "H", "p_draw": "D", "p_away": "A"})
accuracy = (df["pred"] == df["actual"]).mean()


def ll(row):
    if row["actual"] == "H":
        return -np.log(row["p_home"])
    if row["actual"] == "D":
        return -np.log(row["p_draw"])
    return -np.log(row["p_away"])


df["log_loss"] = df.apply(ll, axis=1)

st.metric("Matches", len(df))
st.metric("Accuracy", f"{accuracy*100:.2f}%")
st.metric("Avg log loss", f"{df['log_loss'].mean():.4f}")

st.divider()

st.write("Sample rows")
st.dataframe(df.head(20))
