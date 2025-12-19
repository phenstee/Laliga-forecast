import streamlit as st
import pandas as pd


@st.cache_data
def load_matches():
    df = pd.read_csv("data/processed/matches_clean.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date")


@st.cache_data
def load_latest():
    return pd.read_csv("data/processed/latest_ratings.csv")


def team_last_n(df, team, n=5):
    sub = df[(df["home_team"] == team) | (df["away_team"] == team)].copy()
    sub = sub.sort_values("date", ascending=False).head(n)

    pts = 0
    gf = 0
    ga = 0
    for _, r in sub.iterrows():
        if r["home_team"] == team:
            gf += r["home_goals"]
            ga += r["away_goals"]
            pts += 3 if r["home_goals"] > r["away_goals"] else 1 if r["home_goals"] == r["away_goals"] else 0
        else:
            gf += r["away_goals"]
            ga += r["home_goals"]
            pts += 3 if r["away_goals"] > r["home_goals"] else 1 if r["away_goals"] == r["home_goals"] else 0
    return {"matches": len(sub), "points": pts, "gf": gf, "ga": ga}


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
    return diff, p_home, p_draw, p_away


st.title("Match Preview")

df = load_matches()
ratings = load_latest().set_index("team")["rating"].to_dict()

# Pick teams manually (works even without future fixtures)
teams = sorted(set(df["home_team"]).union(set(df["away_team"])))
home = st.selectbox("Home team", teams, index=0)
away = st.selectbox("Away team", teams, index=1)

r_home = float(ratings.get(home, 1500))
r_away = float(ratings.get(away, 1500))
diff, p_home, p_draw, p_away = probs_with_draw(r_home, r_away)

c1, c2, c3 = st.columns(3)
c1.metric("Home win", f"{p_home*100:.1f}%")
c2.metric("Draw", f"{p_draw*100:.1f}%")
c3.metric("Away win", f"{p_away*100:.1f}%")

st.write("### Why (simple explanation)")
st.write(f"Elo diff (home incl. advantage): **{diff:.1f}** points")
form_home = team_last_n(df, home, n=5)
form_away = team_last_n(df, away, n=5)
st.write({f"{home} last 5": form_home, f"{away} last 5": form_away})
