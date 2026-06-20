from src.tools.excel_tools import load_excel, summarize_dataset, ExcelLoadError


def load_excel_node(state: dict) -> dict:
    try:
        df = load_excel(state["excel_path"])
    except ExcelLoadError as exc:
        raise RuntimeError(str(exc)) from exc

    return {
        "dataframe": df,
        "summary": summarize_dataset(df),
    }