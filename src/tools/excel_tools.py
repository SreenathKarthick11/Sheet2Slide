from pathlib import Path
import pandas as pd


class ExcelLoadError(Exception):
    """Raised when the input file can't be loaded as tabular data."""


def load_excel(path: str) -> pd.DataFrame:
    file_path = Path(path)

    if not file_path.exists():
        raise ExcelLoadError(f"File not found: {path}")

    suffix = file_path.suffix.lower()

    try:
        if suffix in (".xlsx", ".xls", ".xlsm"):
            df = pd.read_excel(file_path)
        elif suffix == ".csv":
            df = pd.read_csv(file_path)
        else:
            raise ExcelLoadError(
                f"Unsupported file type '{suffix}'. Use .xlsx, .xls, .xlsm, or .csv."
            )
    except ExcelLoadError:
        raise
    except Exception as exc:
        raise ExcelLoadError(f"Failed to read '{path}': {exc}") from exc

    if df.empty:
        raise ExcelLoadError(f"'{path}' loaded but contains no rows.")

    # Try to coerce obviously date-like object columns into real datetimes.
    # This makes trend_analysis and chart x-axes much more useful without
    # requiring the user's spreadsheet to already use Excel date formatting.
    for col in df.columns:
        if df[col].dtype == object:
            sample = df[col].dropna().head(20)

            if sample.empty:
                continue

            parsed = pd.to_datetime(sample, errors="coerce", format=None)

            if parsed.notna().mean() > 0.8:
                df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def summarize_dataset(df: pd.DataFrame, sample_rows: int = 3) -> dict:
    """
    A summary rich enough for an LLM to make real chart/analysis decisions,
    not just column names. Includes dtype and a small sample per column so
    the agent can distinguish e.g. a categorical "Region" column from a
    free-text "Notes" column.
    """

    numeric_cols = list(df.select_dtypes(include="number").columns)
    datetime_cols = list(df.select_dtypes(include="datetime64[ns]").columns)
    categorical_cols = [
        c for c in df.columns if c not in numeric_cols and c not in datetime_cols
    ]

    columns_info = []

    for col in df.columns:
        series = df[col]
        sample_values = series.dropna().head(sample_rows).tolist()

        columns_info.append({
            "name": str(col),
            "dtype": str(series.dtype),
            "unique_values": int(series.nunique(dropna=True)),
            "missing_count": int(series.isna().sum()),
            "sample_values": [str(v) for v in sample_values],
        })

    return {
        "rows": int(len(df)),
        "columns": [str(c) for c in df.columns],
        "numeric_columns": [str(c) for c in numeric_cols],
        "datetime_columns": [str(c) for c in datetime_cols],
        "categorical_columns": [str(c) for c in categorical_cols],
        "columns_info": columns_info,
    }