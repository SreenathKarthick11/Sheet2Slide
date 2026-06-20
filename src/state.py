from typing import TypedDict
import pandas as pd


class Sheet2SlideState(TypedDict):

    excel_path: str

    dataframe: pd.DataFrame

    summary: dict

    analysis: dict

    visualization_plan: dict

    chart_paths: list[str]

    slide_plan: list[dict]

    insights: str

    ppt_path: str