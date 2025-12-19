import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


@st.cache_data
def load_history():
    df = pd.read_csv("data/processed/elo_history.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


st.title("Teams")

hist = load_history()
teams = sorted(set(hist["home_team"]).union(set(hist["away_team"])))
team = st.selectbox("Select team", teams)

# Build rating series by taking matches where team was home/away and reading post rating
home_rows = hist[hist["home_team"] == team][["date", "r_home_post"]].rename(
    columns={"r_home_post": "rating"})
away_rows = hist[hist["away_team"] == team][["date", "r_away_post"]].rename(
    columns={"r_away_post": "rating"})
series = pd.concat([home_rows, away_rows]).sort_values("date")

fig = plt.figure()
plt.plot(series["date"], series["rating"])
plt.title(f"Elo rating over time — {team}")
plt.xlabel("Date")
plt.ylabel("Elo")
st.pyplot(fig)

st.write("### Recent matches")
recent = hist[(hist["home_team"] == team) | (hist["away_team"] ==
                                             team)].sort_values("date", ascending=False).head(10)
st.dataframe(recent[["date", "home_team", "away_team",
             "home_goals", "away_goals", "p_home", "p_draw", "p_away"]])
