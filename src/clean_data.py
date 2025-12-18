from pathlib import Path
import pandas as pd

RAW_PATH = Path("data/raw/matches.csv")
OUT_PATH = Path("data/processed/matches_clean.csv")

COLUMN_MAP = {
    "Date": "date",
    "HomeTeam": "home_team",
    "AwayTeam": "away_team",
    "FTHG": "home_goals",
    "FTAG": "away_goals",
    "FTR": "result"
}


def main():
    df = pd.read_csv(RAW_PATH)

    # Keep only the columns we care about (ignore odds, refs, etc.)
    keep = [c for c in COLUMN_MAP.keys() if c in df.columns]
    missing = [c for c in COLUMN_MAP.keys() if c not in df.columns]
    if missing:
        print("Missing expected columns:", missing)
        print("Available columns:", list(df.columns))
        raise SystemExit("Fix COLUMN_MAP to match your csv headers. ")

    df = df[keep].rename(columns=COLUMN_MAP)

    # Parse dates (football-data style is day-first usually)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    # Convert goals to numeric
    df["home_goals"] = pd.to_numeric(df["home_goals"], errors="coerce")
    df["away_goals"] = pd.to_numeric(df["away_goals"], errors="coerce")

    # Drop rows with missing critical data
    df = df.dropna(subset=["date", "home_team",
                   "away_team", "home_goals", "away_goals"])

    # Ensure correct data types
    df["home_goals"] = df["home_goals"].astype(int)
    df["away_goals"] = df["away_goals"].astype(int)

    # If result column exists, keep it; otherwise create it from goals
    if "result" not in df.columns:
        def compute_result(row):
            if row["home_goals"] > row["away_goals"]:
                return "H"
            elif row["home_goals"] < row["away_goals"]:
                return "A"
            else:
                return "D"
        df["result"] = df.apply(compute_result, axis=1)
    else:
        df["result"] = df["result"].astype(str).str.upper().str.strip()

    # Sort chronologically
    df = df.sort_values("date").reset_index(drop=True)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)

    print("Saved:", OUT_PATH)
    print(df.head())
    print("Clean rows:", len(df))


if __name__ == "__main__":
    main()
