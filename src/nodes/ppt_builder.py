from src.ppt.ppt_builder import create_ppt


def build_ppt_node(state: dict) -> dict:
    ppt_path = create_ppt(
        slide_plan=state.get("slide_plan", []),
    )

    return {
        "ppt_path": ppt_path,
    }