from pathlib import Path
import pandas as pd
import numpy as np

HIST_PATH = Path("data/processed/elo_history.csv")


def actual_outcome(row):
    if row["home_goals"] > row["away_goals"]:
        return "H"
    if row["home_goals"] < row["away_goals"]:
        return "A"
    return "D"


def main():
    df = pd.read_csv(HIST_PATH)

    # Safety against log(0)
    eps = 1e-12
    df["p_home"] = df["p_home"].clip(eps, 1 - eps)
    df["p_away"] = df["p_away"].clip(eps, 1 - eps)
    df["p_draw"] = df["p_draw"].clip(eps, 1 - eps)

    df["actual"] = df.apply(actual_outcome, axis=1)

    def pred_label(row):
        probs = {"H": row["p_home"], "D": row["p_draw"], "A": row["p_away"]}
        return max(probs, key=probs.get)

    df["pred"] = df.apply(pred_label, axis=1)
    accuracy = (df["pred"] == df["actual"]).mean()

    # Log loss (multiclass)
    def log_loss(row):
        if row["actual"] == "H":
            return -np.log(row["p_home"])
        elif row["actual"] == "A":
            return -np.log(row["p_away"])
        else:
            return -np.log(row["p_draw"])

    df["log_loss"] = df.apply(log_loss, axis=1)
    avg_log_loss = df["log_loss"].mean()

    print("Matches:", len(df))
    print("Accuracy (argmax):", round(float(accuracy), 4))
    print("Avg log loss:", round(float(avg_log_loss), 4))


if __name__ == "__main__":
    main()
