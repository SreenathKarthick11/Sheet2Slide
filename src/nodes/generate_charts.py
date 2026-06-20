from src.tools.chart_tools import (
    generate_charts_from_plan
)


def generate_charts_node(state):

    charts = generate_charts_from_plan(

        state["dataframe"]
    )

    return {

        "chart_paths": charts
    }