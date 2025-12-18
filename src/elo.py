from pathlib import Path
import pandas as pd
import numpy as np

IN_PATH = Path("data/processed/matches_clean.csv")
OUT_HISTORY = Path("data/processed/elo_history.csv")
OUT_LATEST = Path("data/processed/elo_latest_rating.csv")

BASE_RATING = 1500.0
K = 20.0
HOME_ADV = 60


def clamp(x, lo, hi):
    return max(lo, min(x, hi))


def expected_home_nodraw(r_home, r_away):
    diff = (r_home + HOME_ADV) - r_away
    return 1.0 / (1.0 + 10 ** (-diff / 400.0))


def probs_with_draw(r_home, r_away):
    diff = (r_home + HOME_ADV) - r_away
    p_home_nodraw = expected_home_nodraw(r_home, r_away)

    # Simple draw heuristic: draw more likely when teams are close
    p_draw = clamp(0.28 - abs(diff) / 2000.0, 0.15, 0.30)

    p_home = (1 - p_draw) * p_home_nodraw
    p_away = (1 - p_draw) * (1 - p_home_nodraw)
    return p_home, p_away, p_draw


def outcome_score_home(result):
    # results: H, A, D
    if result == "H":
        return 1.0
    elif result == "A":
        return 0.0
    else:
        return 0.5


def main():
    df = pd.read_csv(IN_PATH)
    df["date"] = pd.to_datetime(df["date"])

    teams = sorted(set(df["home_team"]).union(set(df["away_team"])))
    ratings = {t: BASE_RATING for t in teams}

    rows = []

    for _, m in df.iterrows():
        date = m["date"]
        home = m["home_team"]
        away = m["away_team"]
        hg = int(m["home_goals"])
        ag = int(m["away_goals"])
        result = str(m["result"]).upper().strip()

        r_home = ratings.get(home, BASE_RATING)
        r_away = ratings.get(away, BASE_RATING)

        p_home, p_away, p_draw = probs_with_draw(r_home, r_away)
        s_home = outcome_score_home(result)
        e_home = expected_home_nodraw(r_home, r_away)

        # Elo update
        r_home_new = r_home + K * (s_home - e_home)
        r_away_new = r_away + K * ((1 - s_home) - (1 - e_home))

        ratings[home] = r_home_new
        ratings[away] = r_away_new

        rows.append({
            "date": date,
            "home_team": home,
            "away_team": away,
            "home_goals": hg,
            "away_goals": ag,
            "result": result,
            "r_home_pre": r_home,
            "r_away_pre": r_away,
            "p_home": p_home,
            "p_away": p_away,
            "p_draw": p_draw,
            "r_home_post": r_home_new,
            "r_away_post": r_away_new,
        })

    hist = pd.DataFrame(rows)
    for col in ["r_home_pre", "r_away_pre", "r_home_post", "r_away_post"]:
        hist[col] = hist[col].round(1)

    OUT_HISTORY.parent.mkdir(parents=True, exist_ok=True)
    hist.to_csv(OUT_HISTORY, index=False)

    latest = (
        pd.DataFrame({"Teams": list(ratings.keys()),
                     "Ratings": list(ratings.values())})
        .sort_values("Ratings", ascending=False)
        .reset_index(drop=True)
    )
    latest["Ratings"] = latest["Ratings"].round(1)
    latest.to_csv(OUT_LATEST, index=False)

    print("Saved:", OUT_HISTORY)
    print("Saved:", OUT_LATEST)
    print("\nTop 10 ratings:")
    print(latest.head(10))


if __name__ == "__main__":
    main()
