from src.tools.analysis_tools import run_analysis


def analysis_node(state: dict) -> dict:
    plan = state.get("analysis_plan", {})
    requested = plan.get("required_statistics")

    analysis = run_analysis(state["dataframe"], requested=requested)

    return {
        "analysis": analysis,
    }