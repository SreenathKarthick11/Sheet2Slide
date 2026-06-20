from pathlib import Path
import re
import matplotlib
matplotlib.use("Agg")  # headless rendering, no display backend needed
import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output" / "charts"

# A small, consistent palette so charts feel like they belong to the same
# report rather than each using matplotlib's default cycle.
PRIMARY_COLOR = "#1E2761"
ACCENT_COLOR = "#F96167"
PALETTE = ["#1E2761", "#F96167", "#97BC62", "#F9E795", "#065A82", "#A26769"]


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", text.strip().lower())
    return slug.strip("_") or "chart"


def _safe_title(spec: dict) -> str:
    if spec.get("title"):
        return spec["title"]

    if spec.get("column"):
        return f"{spec['column']} ({spec['chart_type']})"

    if spec.get("x_column") and spec.get("y_column"):
        return f"{spec['y_column']} vs {spec['x_column']}"

    return spec["chart_type"].title()


def render_chart(df: pd.DataFrame, spec: dict, index: int, include_title: bool = False) -> dict | None:
    """
    Render a single validated ChartSpec to a PNG file.

    `include_title` controls whether the chart image itself carries a
    matplotlib title -- by default it doesn't, since the chart is always
    placed under a slide title in the deck and a duplicate title wastes
    vertical space. Set True only if the chart might be viewed standalone.

    Returns a manifest entry dict on success, or None if the chart
    couldn't be rendered (e.g. missing/empty column data) -- callers
    should skip None results rather than failing the whole pipeline over
    one bad chart.
    """

    chart_type = spec["chart_type"]
    title = _safe_title(spec)

    try:
        plt.figure(figsize=(8, 4.5))

        if chart_type == "line":
            x_col, y_col = spec.get("x_column"), spec.get("y_column")
            if not x_col or not y_col:
                return None
            data = df[[x_col, y_col]].dropna()
            if data.empty:
                return None
            data = data.sort_values(x_col)
            plt.plot(data[x_col], data[y_col], color=PRIMARY_COLOR, linewidth=2)
            plt.xlabel(x_col)
            plt.ylabel(y_col)

        elif chart_type == "scatter":
            x_col, y_col = spec.get("x_column"), spec.get("y_column")
            if not x_col or not y_col:
                return None
            data = df[[x_col, y_col]].dropna()
            if data.empty:
                return None
            plt.scatter(data[x_col], data[y_col], color=PRIMARY_COLOR, alpha=0.7)
            plt.xlabel(x_col)
            plt.ylabel(y_col)

        elif chart_type == "bar":
            if spec.get("x_column") and spec.get("y_column"):
                x_col, y_col = spec["x_column"], spec["y_column"]
                data = df[[x_col, y_col]].dropna()
                if data.empty:
                    return None
                grouped = data.groupby(x_col)[y_col].mean().sort_values(ascending=False).head(12)
                plt.bar(grouped.index.astype(str), grouped.values, color=PRIMARY_COLOR)
                plt.xlabel(x_col)
                plt.ylabel(f"mean {y_col}")
                plt.xticks(rotation=30, ha="right")
            elif spec.get("column"):
                col = spec["column"]
                series = df[col].dropna()
                if series.empty:
                    return None
                if pd.api.types.is_numeric_dtype(series):
                    counts = series.value_counts().sort_index().head(15)
                else:
                    counts = series.value_counts().head(15)
                plt.bar(counts.index.astype(str), counts.values, color=PRIMARY_COLOR)
                plt.xlabel(col)
                plt.ylabel("count")
                plt.xticks(rotation=30, ha="right")
            else:
                return None

        elif chart_type == "histogram":
            col = spec.get("column")
            if not col:
                return None
            series = df[col].dropna()
            if series.empty or not pd.api.types.is_numeric_dtype(series):
                return None
            plt.hist(series, bins=min(20, max(5, series.nunique())), color=PRIMARY_COLOR, edgecolor="white")
            plt.xlabel(col)
            plt.ylabel("frequency")

        elif chart_type == "box":
            col = spec.get("column")
            if not col:
                return None
            series = df[col].dropna()
            if series.empty or not pd.api.types.is_numeric_dtype(series):
                return None
            plt.boxplot(series, vert=True, patch_artist=True,
                        boxprops=dict(facecolor=PRIMARY_COLOR, alpha=0.6))
            plt.ylabel(col)

        elif chart_type == "pie":
            col = spec.get("column")
            if not col:
                return None
            series = df[col].dropna()
            if series.empty:
                return None
            counts = series.value_counts().head(8)
            if counts.empty:
                return None
            plt.pie(
                counts.values,
                labels=counts.index.astype(str),
                autopct="%1.0f%%",
                colors=PALETTE,
            )

        else:
            return None

        if include_title:
            plt.title(title)

        plt.tight_layout()

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{index:02d}_{_slugify(title)}.png"
        chart_path = OUTPUT_DIR / filename
        plt.savefig(chart_path, dpi=150)
        plt.close()

        return {
            "path": str(chart_path),
            "chart_type": chart_type,
            "title": title,
            "caption": spec.get("rationale") or "",
            "columns": [c for c in (spec.get("column"), spec.get("x_column"), spec.get("y_column")) if c],
        }

    except Exception:
        plt.close()
        return None


def generate_charts_from_specs(df: pd.DataFrame, chart_specs: list[dict]) -> list[dict]:
    """Renders every validated chart spec, skipping any that fail."""

    manifest = []

    for i, spec in enumerate(chart_specs):
        entry = render_chart(df, spec, i)
        if entry is not None:
            manifest.append(entry)

    return manifest