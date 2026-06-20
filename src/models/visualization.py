from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal


ChartType = Literal["line", "bar", "scatter", "box", "histogram", "pie"]


class ChartSpec(BaseModel):
    """
    A single chart the agent wants generated.

    `column` / `x_column` / `y_column` must refer to real column names in
    the dataset -- this gets validated against the actual dataframe in
    `agents/visualization_planner.py` before any chart is rendered, since
    an LLM (especially a small local one) will sometimes hallucinate
    column names that look plausible but don't exist.
    """

    chart_type: ChartType

    # For single-column charts (histogram, box, pie, bar-of-value-counts)
    column: Optional[str] = None

    # For two-column charts (line trend, scatter, bar comparison)
    x_column: Optional[str] = None
    y_column: Optional[str] = None

    title: Optional[str] = Field(
        default=None,
        description="Short, human-readable chart title.",
    )

    rationale: Optional[str] = Field(
        default=None,
        description="Why this chart is useful for this dataset.",
    )

    @field_validator("chart_type")
    @classmethod
    def _lower(cls, v: str) -> str:
        return v.lower().strip()


class VisualizationPlan(BaseModel):
    charts: List[ChartSpec] = Field(default_factory=list)