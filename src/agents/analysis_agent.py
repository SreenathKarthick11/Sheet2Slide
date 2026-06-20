from src.llm import llm
from src.models.analysis import AnalysisPlan

VALID_CATEGORIES = {"summary", "correlation", "outliers", "trend", "categorical"}

structured_llm = llm.with_structured_output(AnalysisPlan)


def analysis_agent(state: dict) -> dict:
    summary = state["summary"]

    prompt = f"""
    You are deciding which analysis categories are worth running on this dataset.

    Dataset summary:
    Rows: {summary['rows']}
    Numeric columns: {summary['numeric_columns']}
    Datetime columns: {summary['datetime_columns']}
    Categorical columns: {summary['categorical_columns']}

    Available categories (choose any that apply, usually most of them):
    - "summary": basic mean/median/min/max/std for numeric columns. Almost always useful.
    - "correlation": relationships between numeric columns. Only useful if there are 2+ numeric columns.
    - "outliers": unusual extreme values in numeric columns.
    - "trend": change over time/sequence. Only useful if there's a datetime or clearly sequential column.
    - "categorical": breakdown of categorical column values. Only useful if there are categorical columns.

    Return the list of categories to run, with brief reasoning.
    """

    reasoning = ""

    try:
        plan = structured_llm.invoke(prompt)
        categories = [c for c in plan.required_statistics if c in VALID_CATEGORIES]
        reasoning = plan.reasoning
    except Exception:
        categories = []

    # Fallback: if the LLM returned nothing usable, run everything that's
    # structurally possible rather than producing an empty analysis.
    if not categories:
        categories = list(VALID_CATEGORIES)

    return {
        "analysis_plan": {
            "required_statistics": categories,
            "reasoning": reasoning,
        }
    }