from src.llm import llm
from src.models.visualization import VisualizationPlan

structured_llm = llm.with_structured_output(VisualizationPlan)

MAX_CHARTS = 6


def _validate_spec(spec: dict, columns_info: dict, datetime_cols: set, numeric_cols: set) -> dict | None:
    """
    Confirms a chart spec only references real columns and that the
    column types make sense for the requested chart type. Returns a
    cleaned dict, or None if the spec can't be salvaged.
    """

    chart_type = spec.get("chart_type")
    column = spec.get("column")
    x_col = spec.get("x_column")
    y_col = spec.get("y_column")

    def exists(name):
        return name is not None and name in columns_info

    if chart_type in ("histogram", "box", "pie") and column is None and x_col:
        # Model sometimes puts a single column in x_column instead of column
        # for chart types that only ever take one axis.
        column = x_col
        x_col = None
        y_col = None

    if chart_type == "bar" and column is None and x_col and not y_col:
        # Bar charts have two valid forms: (column) for a value-count bar,
        # or (x_column + y_column) for a categorical-vs-numeric comparison.
        # Only remap x_column -> column when y_column wasn't also supplied
        # -- otherwise this would silently discard a valid two-axis request.
        column = x_col
        x_col = None

    if chart_type in ("line", "scatter") and (not x_col or not y_col):
        return None

    if chart_type in ("line", "scatter"):
        if not exists(x_col) or not exists(y_col):
            return None
        if chart_type == "line" and y_col not in numeric_cols:
            return None

    if chart_type in ("histogram", "box"):
        if not exists(column) or column not in numeric_cols:
            return None

    if chart_type == "pie":
        if not exists(column):
            return None
        # Pie charts only make sense for low-cardinality columns.
        if columns_info[column]["unique_values"] > 10:
            return None

    if chart_type == "bar":
        if x_col and y_col:
            if not exists(x_col) or not exists(y_col) or y_col not in numeric_cols:
                return None
        elif column:
            if not exists(column):
                return None
        else:
            return None

    return {
        "chart_type": chart_type,
        "column": column,
        "x_column": x_col,
        "y_column": y_col,
        "title": spec.get("title"),
        "rationale": spec.get("rationale"),
    }


def visualization_planner(state: dict) -> dict:
    summary = state["summary"]
    analysis = state.get("analysis", {})

    columns_info = {c["name"]: c for c in summary["columns_info"]}
    datetime_cols = set(summary["datetime_columns"])
    numeric_cols = set(summary["numeric_columns"])

    prompt = f"""
    You are picking the most informative charts for this dataset. Use ONLY
    the exact column names given below -- never invent a column name.

    Columns (name: dtype, unique values, sample values):
    {[
        f"{c['name']}: {c['dtype']}, {c['unique_values']} unique, e.g. {c['sample_values']}"
        for c in summary["columns_info"]
    ]}

    Numeric columns: {summary['numeric_columns']}
    Datetime columns: {summary['datetime_columns']}
    Categorical columns: {summary['categorical_columns']}

    Notable correlations found: {analysis.get('correlation', {}).get('notable_pairs', [])}
    Trend info found: {analysis.get('trend', {})}
    Outliers found: {list(analysis.get('outliers', {}).keys())}

    Chart type guide:
    - "line": needs x_column (ideally datetime/sequential) and y_column (numeric). Good for trends.
    - "scatter": needs x_column and y_column (both numeric). Good for correlations.
    - "bar": needs either (x_column=categorical, y_column=numeric) for comparisons,
      or just column for a value-count bar chart.
    - "histogram": needs column (numeric). Shows distribution.
    - "box": needs column (numeric). Shows spread and outliers.
    - "pie": needs column (categorical with <= 8 unique values). Shows proportions.

    Propose at most {MAX_CHARTS} charts, prioritizing the most insightful ones
    given the analysis above. Give each a short title and a one-sentence
    rationale.
    """

    try:
        plan = structured_llm.invoke(prompt)
        raw_specs = [c.model_dump() for c in plan.charts]
    except Exception:
        raw_specs = []

    validated = []
    for spec in raw_specs:
        cleaned = _validate_spec(spec, columns_info, datetime_cols, numeric_cols)
        if cleaned:
            validated.append(cleaned)
        if len(validated) >= MAX_CHARTS:
            break

    # Fallback: if the LLM produced nothing usable, build a small set of
    # safe default charts so the deck never ships with zero visuals.
    if not validated:
        validated = _default_chart_specs(summary, numeric_cols, datetime_cols)

    return {
        "visualization_plan": {"charts": raw_specs},
        "chart_specs": validated,
    }


def _default_chart_specs(summary: dict, numeric_cols: set, datetime_cols: set) -> list[dict]:
    specs = []
    numeric_list = list(numeric_cols)
    datetime_list = list(datetime_cols)

    if datetime_list and numeric_list:
        specs.append({
            "chart_type": "line",
            "column": None,
            "x_column": datetime_list[0],
            "y_column": numeric_list[0],
            "title": f"{numeric_list[0]} over time",
            "rationale": "Default trend chart.",
        })

    for col in numeric_list[:3]:
        specs.append({
            "chart_type": "histogram",
            "column": col,
            "x_column": None,
            "y_column": None,
            "title": f"Distribution of {col}",
            "rationale": "Default distribution chart.",
        })

    return specs[:MAX_CHARTS]