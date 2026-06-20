"""
Deterministic analysis functions.

These never go through the LLM -- the numbers must be trustworthy.
The LLM only decides *which* of these to call (see agents/analysis_agent.py)
and later narrates what they mean.
"""

import numpy as np
import pandas as pd


def numeric_summary(df: pd.DataFrame) -> dict:
    """Per-column mean/median/min/max/std for every numeric column."""

    numeric_cols = df.select_dtypes(include="number").columns
    result = {}

    for col in numeric_cols:
        series = df[col].dropna()

        if series.empty:
            continue

        result[col] = {
            "mean": round(float(series.mean()), 2),
            "median": round(float(series.median()), 2),
            "max": round(float(series.max()), 2),
            "min": round(float(series.min()), 2),
            "std": round(float(series.std()), 2) if len(series) > 1 else 0.0,
            "count": int(series.count()),
        }

    return result


def correlation_analysis(df: pd.DataFrame, threshold: float = 0.5) -> dict:
    """
    Pairwise Pearson correlation between numeric columns.

    Returns both the full correlation matrix and a filtered list of
    "notable" pairs whose |correlation| >= threshold, since a full matrix
    on a wide dataset is too noisy to put in a slide directly.
    """

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.shape[1] < 2:
        return {"matrix": {}, "notable_pairs": []}

    corr = numeric_df.corr(numeric_only=True)

    notable_pairs = []
    cols = corr.columns

    for i, col_a in enumerate(cols):
        for col_b in cols[i + 1:]:
            value = corr.loc[col_a, col_b]

            if pd.isna(value):
                continue

            if abs(value) >= threshold:
                notable_pairs.append({
                    "column_a": col_a,
                    "column_b": col_b,
                    "correlation": round(float(value), 3),
                    "direction": "positive" if value > 0 else "negative",
                })

    notable_pairs.sort(key=lambda p: abs(p["correlation"]), reverse=True)

    return {
        "matrix": corr.round(3).to_dict(),
        "notable_pairs": notable_pairs,
    }


def outlier_analysis(df: pd.DataFrame, iqr_multiplier: float = 1.5) -> dict:
    """
    IQR-based outlier detection per numeric column.

    A value is flagged as an outlier if it falls outside
    [Q1 - k*IQR, Q3 + k*IQR]. This is a standard, simple heuristic that
    doesn't require any distributional assumptions.
    """

    numeric_cols = df.select_dtypes(include="number").columns
    result = {}

    for col in numeric_cols:
        series = df[col].dropna()

        if len(series) < 4:
            # Not enough data to meaningfully compute quartiles.
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_bound = q1 - iqr_multiplier * iqr
        upper_bound = q3 + iqr_multiplier * iqr

        outliers = series[(series < lower_bound) | (series > upper_bound)]

        if len(outliers) == 0:
            continue

        result[col] = {
            "count": int(len(outliers)),
            "pct_of_rows": round(100 * len(outliers) / len(series), 2),
            "lower_bound": round(float(lower_bound), 2),
            "upper_bound": round(float(upper_bound), 2),
            "example_values": [round(float(v), 2) for v in outliers.head(5).tolist()],
        }

    return result


def _looks_like_time_axis(series: pd.Series) -> bool:
    """Heuristic: is this column a reasonable x-axis for a trend (date or monotonically-ish ordered)?"""

    if pd.api.types.is_datetime64_any_dtype(series):
        return True

    if pd.api.types.is_numeric_dtype(series):
        return True

    return False


def trend_analysis(df: pd.DataFrame) -> dict:
    """
    Simple linear-trend detection.

    Uses the first column that looks like a time/sequence axis (datetime
    or numeric) against every other numeric column, fitting a 1-degree
    polynomial (least-squares line) to estimate direction and magnitude.
    This is intentionally simple -- it's meant to surface "this is
    generally going up/down", not to forecast.
    """

    if df.shape[0] < 3:
        return {}

    x_col = None

    for col in df.columns:
        if _looks_like_time_axis(df[col]):
            x_col = col
            break

    if x_col is None:
        return {}

    numeric_cols = [c for c in df.select_dtypes(include="number").columns if c != x_col]

    if not numeric_cols:
        return {}

    # Build a numeric x-axis (datetimes get converted to ordinal day counts).
    x_raw = df[x_col]

    if pd.api.types.is_datetime64_any_dtype(x_raw):
        x = x_raw.map(lambda d: d.toordinal() if pd.notna(d) else np.nan)
    else:
        x = x_raw.astype(float)

    result = {"x_column": x_col, "trends": {}}

    # Sort by the x-axis once up front -- spreadsheet rows aren't guaranteed
    # to already be in chronological/sequential order, and start/end-based
    # direction detection is meaningless on unsorted data.
    order = np.argsort(x.to_numpy(dtype=float), kind="stable")
    x_sorted = x.to_numpy(dtype=float)[order]

    for col in numeric_cols:
        y = df[col].to_numpy(dtype=float)[order]
        x_vals_full = x_sorted

        mask = ~np.isnan(x_vals_full) & ~np.isnan(y)

        if mask.sum() < 3:
            continue

        x_vals = x_vals_full[mask]
        y_vals = y[mask]

        if np.unique(x_vals).size < 2:
            continue

        slope, intercept = np.polyfit(x_vals, y_vals, 1)

        start_value = y_vals[0]
        end_value = y_vals[-1]

        # Direction is judged from the median of the first vs last quarter
        # of points (median, not mean, so a single outlier landing in
        # either window can't flip the detected direction) -- this reflects
        # the dataset's real overall movement better than the fitted slope,
        # which an outlier can also distort.
        n = len(y_vals)
        window = max(1, n // 4)
        early_level = np.median(y_vals[:window])
        late_level = np.median(y_vals[-window:])

        if early_level != 0:
            relative_change = (late_level - early_level) / abs(early_level)
        else:
            relative_change = late_level - early_level

        if relative_change > 0.05:
            direction = "increasing"
        elif relative_change < -0.05:
            direction = "decreasing"
        else:
            direction = "flat"

        pct_change = None
        if y_vals[0] != 0:
            pct_change = round(100 * (y_vals[-1] - y_vals[0]) / abs(y_vals[0]), 2)

        result["trends"][col] = {
            "direction": direction,
            "slope": round(float(slope), 4),
            "start_value": round(float(y_vals[0]), 2),
            "end_value": round(float(y_vals[-1]), 2),
            "pct_change": pct_change,
        }

    return result if result["trends"] else {}


def categorical_analysis(df: pd.DataFrame, max_categories: int = 8) -> dict:
    """
    Value-count breakdown for non-numeric, non-datetime columns with a
    manageable number of unique values. Columns with very high cardinality
    (e.g. free-text or unique IDs) are skipped since a breakdown of them
    isn't useful on a slide.
    """

    result = {}

    candidate_cols = df.select_dtypes(exclude=["number", "datetime64[ns]"]).columns

    for col in candidate_cols:
        series = df[col].dropna()

        if series.empty:
            continue

        unique_count = series.nunique()

        # Skip likely free-text / ID columns.
        if unique_count > max_categories * 3 or unique_count == len(series):
            continue

        counts = series.value_counts().head(max_categories)

        result[col] = {
            "unique_values": int(unique_count),
            "top_categories": {str(k): int(v) for k, v in counts.items()},
            "most_common": str(counts.index[0]),
        }

    return result


def run_analysis(df: pd.DataFrame, requested: list[str] | None = None) -> dict:
    """
    Dispatcher used by analysis_node. `requested` comes from the
    analysis_agent's AnalysisPlan; if empty/None, runs everything.
    """

    requested = set(requested) if requested else {
        "summary", "correlation", "outliers", "trend", "categorical",
    }

    analysis: dict = {}

    if "summary" in requested:
        analysis["summary"] = numeric_summary(df)

    if "correlation" in requested:
        analysis["correlation"] = correlation_analysis(df)

    if "outliers" in requested:
        analysis["outliers"] = outlier_analysis(df)

    if "trend" in requested:
        analysis["trend"] = trend_analysis(df)

    if "categorical" in requested:
        analysis["categorical"] = categorical_analysis(df)

    return analysis