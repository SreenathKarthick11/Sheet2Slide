from pydantic import BaseModel
from typing import List


class ChartSpec(BaseModel):

    chart_type: str
    column: str


class VisualizationPlan(BaseModel):

    charts: List[ChartSpec]