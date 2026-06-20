from pydantic import BaseModel
from typing import List


class Slide(BaseModel):

    title: str
    content: str


class StoryPlan(BaseModel):

    slides: List[Slide]