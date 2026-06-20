from pydantic import BaseModel, Field
from typing import List


class AnalysisPlan(BaseModel):
    """
    What the agent thinks is worth computing.

    The actual numbers are always computed deterministically by
    `tools/analysis_tools.py` -- this plan only influences *which*
    categories of analysis get run (e.g. skip correlation if the agent
    decides there's nothing interesting to correlate). The LLM is never
    trusted to compute statistics itself.
    """

    required_statistics: List[str] = Field(
        default_factory=list,
        description=(
            "Categories of analysis to run. Valid values: "
            "'summary', 'correlation', 'outliers', 'trend', 'categorical'."
        ),
    )

    reasoning: str = Field(
        default="",
        description="Brief reasoning for the chosen statistics.",
    )