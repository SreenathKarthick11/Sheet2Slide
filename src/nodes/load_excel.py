from src.tools.excel_tools import (
    load_excel,
    summarize_dataset
)



def load_excel_node(state):

    df = load_excel(
        state["excel_path"]
    )

    return {

        "dataframe": df,

        "summary":
            summarize_dataset(df)
    }



