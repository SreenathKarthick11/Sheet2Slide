from typing import TypedDict, Optional
import pandas as pd


class Sheet2SlideState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.

    `total=False` because most fields are populated incrementally as the
    graph progresses -- only `excel_path` is guaranteed to exist at the
    start.
    """

    # --- input ---
    excel_path: str

    # --- load_excel ---
    dataframe: pd.DataFrame
    summary: dict

    # --- analysis_node ---
    analysis: dict

    # --- visualization_planner (agent) ---
    visualization_plan: dict          # raw plan as proposed by the LLM
    chart_specs: list[dict]           # plan filtered/validated against the dataframe

    # --- generate_charts ---
    chart_paths: list[str]            # charts that were actually rendered
    chart_manifest: list[dict]        # {path, chart_type, columns, caption} for rendered charts

    # --- story_agent (agent) ---
    slide_plan: list[dict]

    # --- build_ppt ---
    ppt_path: str

    # --- bookkeeping ---
    errors: list[str]
    excel_path_resolved: Optional[str]