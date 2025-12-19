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


st.title("Match Predictions")

df = load_matches()
ratings = load_latest().set_index("team")["rating"].to_dict()

# Pick teams manually (works even without future fixtures)
teams = sorted(set(df["home_team"]).union(set(df["away_team"])))
home = st.selectbox("Home team", teams, index=0)
away = st.selectbox("Away team", teams, index=1)

r_home = float(ratings.get(home, 1500))
r_away = float(ratings.get(away, 1500))
diff, p_home, p_draw, p_away = probs_with_draw(r_home, r_away)

left, right = st.columns([2, 1])
with left:
    st.markdown("### Probability")
    c1, c2, c3 = st.columns(3)
    c1.metric("Home win", f"{p_home*100:.1f}%")
    c2.metric("Draw", f"{p_draw*100:.1f}%")
    c3.metric("Away win", f"{p_away*100:.1f}%")
    st.progress(int(p_home*100))
    st.progress(int(p_draw*100))
    st.progress(int(p_away*100))

with right:
    st.markdown("### Quick stats")
    st.write(f"Elo diff (home incl. advantage): **{diff:.1f}** points")

    # Present last-n stats as friendly metrics instead of raw dicts
    home_stats = team_last_n(df, home, n=5)
    away_stats = team_last_n(df, away, n=5)

    left_box, right_box = st.columns(2)
    with left_box:
        st.markdown(f"**{home} (last 5)**")
        st.metric(label="Points", value=home_stats["points"])
        g1, g2 = st.columns(2)
        g1.metric("GF", home_stats["gf"])
        g2.metric("GA", home_stats["ga"])
        st.caption(f"Matches: {home_stats['matches']}")

    with right_box:
        st.markdown(f"**{away} (last 5)**")
        st.metric(label="Points", value=away_stats["points"])
        g1, g2 = st.columns(2)
        g1.metric("GF", away_stats["gf"])
        g2.metric("GA", away_stats["ga"])
        st.caption(f"Matches: {away_stats['matches']}")
