import pandas as pd


def load_excel(file_path: str) -> pd.DataFrame:
    """
    Load Excel file into DataFrame
    """
    return pd.read_excel(file_path)


def summarize_dataset(df: pd.DataFrame) -> dict:
    """
    Generate dataset summary
    """

    return {
        "rows": len(df),
        "columns": list(df.columns),
        "numeric_columns": list(
            df.select_dtypes(include="number").columns
        ),
        "missing_values": df.isnull().sum().to_dict()
    }