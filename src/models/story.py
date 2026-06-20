from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal


SlideLayout = Literal[
    "title",        # big title + subtitle, no body
    "bullets",       # title + bullet list
    "chart",         # title + one chart image + optional short caption
    "stat_callout",  # title + a handful of big highlighted numbers
    "two_column",    # title + bullets on the left, chart on the right
    "closing",       # closing/thank-you slide
]


class StatCallout(BaseModel):
    label: str
    value: str


class Slide(BaseModel):
    layout: SlideLayout = "bullets"

    title: str = ""
    subtitle: Optional[str] = None

    # used by "bullets" and the text side of "two_column"
    bullets: List[str] = Field(default_factory=list)

    # used by "chart" and "two_column" -- must match a path in chart_manifest
    chart_path: Optional[str] = None
    caption: Optional[str] = None

    # used by "stat_callout"
    stats: List[StatCallout] = Field(default_factory=list)

    @field_validator("layout", mode="before")
    @classmethod
    def _normalize_layout(cls, v):
        if isinstance(v, str):
            return v.lower().strip()
        return v


class StoryPlan(BaseModel):
    slides: List[Slide] = Field(default_factory=list)