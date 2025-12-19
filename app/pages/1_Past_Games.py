import streamlit as st
import pandas as pd


@st.cache_data
def load_latest():
    return pd.read_csv("data/processed/latest_ratings.csv")


@st.cache_data
def load_matches():
    df = pd.read_csv("data/processed/matches_clean.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


def expected_home_nodraw(r_home, r_away, home_adv=60.0):
    diff = (r_home + home_adv) - r_away
    return 1.0 / (1.0 + 10 ** (-diff / 400.0))


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def probs_with_draw(r_home, r_away, home_adv=60.0):
    diff = (r_home + home_adv) - r_away
    p_home_nodraw = expected_home_nodraw(r_home, r_away, home_adv)
    p_draw = clamp(0.28 - abs(diff) / 2000.0, 0.15, 0.30)
    p_home = (1 - p_draw) * p_home_nodraw
    p_away = (1 - p_draw) * (1 - p_home_nodraw)
    return p_home, p_draw, p_away


st.title("Past Games")

ratings = load_latest().set_index("team")["rating"].to_dict()
matches = load_matches()

# Use recent matches as selectable history
matches = matches.sort_values("date", ascending=False).head(200)

idx = st.selectbox(
    "Select a match (recent history)",
    matches.index,
    format_func=lambda i: f"{matches.loc[i, 'date'].date()} — {matches.loc[i, 'home_team']} vs {matches.loc[i, 'away_team']}"
)

row = matches.loc[idx]
home = row["home_team"]
away = row["away_team"]
r_home = float(ratings.get(home, 1500))
r_away = float(ratings.get(away, 1500))
p_home, p_draw, p_away = probs_with_draw(r_home, r_away)

st.markdown("### Match probability")
cols = st.columns([1, 1, 1])
cols[0].metric("Home win", f"{p_home*100:.1f}%")
cols[1].metric("Draw", f"{p_draw*100:.1f}%")
cols[2].metric("Away win", f"{p_away*100:.1f}%")

with st.expander("Ratings and details"):
    st.write({"home_team": home, "home_rating": r_home,
              "away_team": away, "away_rating": r_away})
