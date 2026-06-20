from src.llm import llm

from src.models.analysis import (
    AnalysisPlan
)

structured_llm = (
    llm.with_structured_output(
        AnalysisPlan
    )
)


def analysis_agent(state):

    prompt = f"""
    Dataset:

    {state["summary"]}

    What statistics should
    be calculated?
    """

    plan = structured_llm.invoke(
        prompt
    )

    return {
        "analysis_plan":
            plan.model_dump()
    }