from src.tools.chart_tools import generate_charts_from_specs


def generate_charts_node(state: dict) -> dict:
    manifest = generate_charts_from_specs(
        state["dataframe"],
        state.get("chart_specs", []),
    )

    return {
        "chart_manifest": manifest,
        "chart_paths": [entry["path"] for entry in manifest],
    }