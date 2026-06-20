import pandas as pd


def load_excel(path):

    return pd.read_excel(path)


def summarize_dataset(df):

    return {
        "rows": len(df),
        "columns": list(df.columns),
        "numeric_columns":
            list(
                df.select_dtypes(
                    include="number"
                ).columns
            )
    }