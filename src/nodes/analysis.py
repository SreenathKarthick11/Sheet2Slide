from src.tools.analysis_tools import (
    numeric_summary
)

def analysis_node(state):

    analysis = numeric_summary(
        state["dataframe"]
    )

    return {
        "analysis": analysis
    }