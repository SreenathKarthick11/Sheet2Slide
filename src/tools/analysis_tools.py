import pandas as pd


def numeric_summary(df: pd.DataFrame) -> dict:

    numeric_cols = df.select_dtypes(include="number").columns

    analysis = {}

    for col in numeric_cols:

        analysis[col] = {
            "mean": round(df[col].mean(), 2),
            "median": round(df[col].median(), 2),
            "max": round(df[col].max(), 2),
            "min": round(df[col].min(), 2),
            "std": round(df[col].std(), 2)
        }

    return analysis