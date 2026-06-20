from pydantic import BaseModel
from typing import List


class AnalysisPlan(BaseModel):

    required_statistics: List[str]