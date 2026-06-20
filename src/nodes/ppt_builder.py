from src.ppt.ppt_builder import (
    create_ppt
)


def build_ppt_node(state):

    ppt_path = create_ppt(

        summary=state["summary"],

        analysis=state["analysis"],

        charts=state["chart_paths"],

        slide_plan=state["slide_plan"]
    )

    return {
        "ppt_path": ppt_path
    }