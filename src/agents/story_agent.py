from src.llm import llm

from src.models.story import (
    StoryPlan
)

structured_llm = (
    llm.with_structured_output(
        StoryPlan
    )
)


def story_agent(state):

    prompt = f"""
    Dataset:

    {state["summary"]}

    Analysis:

    {state["analysis"]}

    Create presentation outline.
    """

    plan = structured_llm.invoke(
        prompt
    )

    return {

        "slide_plan":
            [
                slide.model_dump()
                for slide in plan.slides
            ]
    }