from src.llm import llm
from src.models.story import StoryPlan

structured_llm = llm.with_structured_output(StoryPlan)


def _format_analysis_for_prompt(analysis: dict) -> str:
    lines = []

    if "summary" in analysis:
        lines.append("Numeric summary:")
        for col, stats in analysis["summary"].items():
            lines.append(f"  - {col}: mean={stats['mean']}, median={stats['median']}, "
                          f"min={stats['min']}, max={stats['max']}, std={stats['std']}")

    if "correlation" in analysis:
        pairs = analysis["correlation"].get("notable_pairs", [])
        if pairs:
            lines.append("Notable correlations:")
            for p in pairs[:5]:
                lines.append(f"  - {p['column_a']} & {p['column_b']}: r={p['correlation']} ({p['direction']})")

    if "outliers" in analysis:
        outliers = analysis["outliers"]
        if outliers:
            lines.append("Outliers:")
            for col, info in outliers.items():
                lines.append(f"  - {col}: {info['count']} outliers ({info['pct_of_rows']}% of rows)")

    if "trend" in analysis:
        trends = analysis["trend"].get("trends", {})
        if trends:
            lines.append(f"Trends (over {analysis['trend'].get('x_column')}):")
            for col, t in trends.items():
                lines.append(f"  - {col}: {t['direction']}, {t['pct_change']}% change "
                              f"({t['start_value']} -> {t['end_value']})")

    if "categorical" in analysis:
        for col, info in analysis["categorical"].items():
            lines.append(f"Category breakdown for {col}: most common = {info['most_common']} "
                          f"(top categories: {info['top_categories']})")

    return "\n".join(lines) if lines else "No notable findings."


def story_agent(state: dict) -> dict:
    summary = state["summary"]
    analysis = state.get("analysis", {})
    chart_manifest = state.get("chart_manifest", [])

    chart_descriptions = [
        f"- path=\"{c['path']}\" type={c['chart_type']} title=\"{c['title']}\" columns={c['columns']}"
        for c in chart_manifest
    ]

    prompt = f"""
    You are designing a presentation deck that tells the story of this dataset.

    Dataset: {summary['rows']} rows, columns: {summary['columns']}

    Analysis findings:
    {_format_analysis_for_prompt(analysis)}

    Available rendered charts (use the exact path string as chart_path if you
    reference one -- do not invent paths, and do not reference a chart that
    isn't listed):
    {chr(10).join(chart_descriptions) if chart_descriptions else "No charts were generated."}

    Design the full slide deck yourself: decide how many slides, what order,
    and what each slide should contain. You have these layouts available:

    - "title": title + subtitle, opens the deck.
    - "bullets": title + a short bulleted list of points.
    - "chart": title + exactly one chart_path (must be from the list above) + optional caption.
    - "stat_callout": title + a few label/value pairs highlighting key numbers.
    - "two_column": title + bullets + one chart_path, side by side.
    - "closing": a short closing/summary slide.

    Guidelines:
    - Start with a "title" slide and end with a "closing" slide.
    - Use every available chart at least once, in whichever layout fits best.
    - Don't pad with filler -- every slide should convey a real finding.
    - Keep bullet points short (under ~15 words each).
    - A typical good deck for this kind of data has 6-10 slides; use your judgment.
    """

    try:
        plan = structured_llm.invoke(prompt)
        slides = [s.model_dump() for s in plan.slides]
    except Exception:
        slides = []

    valid_chart_paths = {c["path"] for c in chart_manifest}
    slides = _sanitize_slides(slides, valid_chart_paths)

    if not slides:
        slides = _fallback_slide_plan(summary, analysis, chart_manifest)

    return {
        "slide_plan": slides,
    }


def _sanitize_slides(slides: list[dict], valid_chart_paths: set) -> list[dict]:
    """Drop chart references to paths that don't actually exist, rather than
    letting a hallucinated path crash the PPT builder later."""

    cleaned = []

    for slide in slides:
        chart_path = slide.get("chart_path")

        if chart_path and chart_path not in valid_chart_paths:
            if slide["layout"] == "chart":
                # Chart slide with no valid chart -- demote to bullets if
                # there's text content, otherwise drop the slide entirely.
                if slide.get("bullets") or slide.get("caption"):
                    slide["layout"] = "bullets"
                    if slide.get("caption") and not slide.get("bullets"):
                        slide["bullets"] = [slide["caption"]]
                    slide["chart_path"] = None
                else:
                    continue
            elif slide["layout"] == "two_column":
                slide["layout"] = "bullets"
                slide["chart_path"] = None
            else:
                slide["chart_path"] = None

        cleaned.append(slide)

    return cleaned


def _fallback_slide_plan(summary: dict, analysis: dict, chart_manifest: list[dict]) -> list[dict]:
    """A minimal, safe deck used only if the LLM call fails entirely."""

    slides = [
        {
            "layout": "title",
            "title": "Data Analysis Report",
            "subtitle": f"{summary['rows']} rows across {len(summary['columns'])} columns",
        },
        {
            "layout": "bullets",
            "title": "Dataset Overview",
            "bullets": [
                f"{summary['rows']} rows, {len(summary['columns'])} columns",
                f"Numeric columns: {', '.join(summary['numeric_columns']) or 'none'}",
                f"Categorical columns: {', '.join(summary['categorical_columns']) or 'none'}",
            ],
        },
    ]

    for chart in chart_manifest:
        slides.append({
            "layout": "chart",
            "title": chart["title"],
            "chart_path": chart["path"],
            "caption": chart.get("caption", ""),
        })

    slides.append({
        "layout": "closing",
        "title": "Thank You",
        "subtitle": "Report generated automatically",
    })

    return slides