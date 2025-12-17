import pandas as pd


def main():
    df = pd.read_csv("data/raw/matches.csv")
    print(df.head())
    print("\nColumns:", list(df.columns))


if __name__ == "__main__":
    main()
