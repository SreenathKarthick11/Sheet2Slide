from pathlib import Path

from pptx import Presentation
from pptx.util import Inches


OUTPUT_FILE = Path(
    "output/reports/report.pptx"
)


def create_ppt(
    summary,
    analysis,
    charts,
    slide_plan,
    insights=""
):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    prs = Presentation()

    # ------------------
    # TITLE SLIDE
    # ------------------

    slide = prs.slides.add_slide(
        prs.slide_layouts[0]
    )

    slide.shapes.title.text = (
        "Excel Analysis Report"
    )

    slide.placeholders[1].text = (
        "Generated Automatically"
    )

    # ------------------
    # SUMMARY SLIDE
    # ------------------

    slide = prs.slides.add_slide(
        prs.slide_layouts[1]
    )

    slide.shapes.title.text = (
        "Dataset Summary"
    )

    body = slide.placeholders[1]

    body.text = (
        f"Rows: {summary['rows']}\n"
        f"Columns: {', '.join(summary['columns'])}\n"
        f"Numeric Columns: "
        f"{', '.join(summary['numeric_columns'])}"
    )

    # ------------------
    # ANALYSIS SLIDE
    # ------------------

    slide = prs.slides.add_slide(
        prs.slide_layouts[1]
    )

    slide.shapes.title.text = (
        "Statistics"
    )

    body = slide.placeholders[1]

    stats_text = ""

    for col, stats in analysis.items():

        stats_text += (
            f"{col}\n"
            f"Mean: {stats['mean']}\n"
            f"Median: {stats['median']}\n"
            f"Max: {stats['max']}\n"
            f"Min: {stats['min']}\n\n"
        )

    body.text = stats_text

    # ------------------
    # CHART SLIDES
    # ------------------

    for chart in charts:

        slide = prs.slides.add_slide(
            prs.slide_layouts[5]
        )

        slide.shapes.title.text = (
            Path(chart).stem
        )

        slide.shapes.add_picture(
            chart,
            Inches(1),
            Inches(1.2),
            width=Inches(6)
        )

    # ------------------
    # INSIGHTS
    # ------------------

    slide = prs.slides.add_slide(
        prs.slide_layouts[1]
    )

    slide.shapes.title.text = (
        "Insights"
    )

    body = slide.placeholders[1]

    body.text = insights

    prs.save(OUTPUT_FILE)

    return str(OUTPUT_FILE)