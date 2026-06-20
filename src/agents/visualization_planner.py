from src.llm import llm

from src.models.visualization import (
    VisualizationPlan
)

structured_llm = (
    llm.with_structured_output(
        VisualizationPlan
    )
)


def visualization_planner(state):

    prompt = f"""
    Dataset Summary:

    {state["summary"]}

    Analysis:

    {state["analysis"]}

    Select useful charts.
    """

    plan = structured_llm.invoke(
        prompt
    )

    return {
        "visualization_plan":
            plan.model_dump()
    }