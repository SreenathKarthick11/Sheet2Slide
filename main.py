from src.excel_reader import (
    load_excel,
    summarize_dataset
)

from src.analyzer import (
    analyze_data
)

from src.chart_generator import (
    generate_charts
)

from src.insight_generator import (
    generate_insights
)

from src.ppt_generator import (
    create_ppt
)


EXCEL_FILE = "data/sample.xlsx"


def main():

    print("Loading Excel...")

    df = load_excel(EXCEL_FILE)

    print("Summarizing dataset...")

    summary = summarize_dataset(df)

    print("Analyzing data...")

    analysis = analyze_data(df)

    print("Generating charts...")

    charts = generate_charts(df)

    print("Generating insights...")

    insights = generate_insights(
        analysis
    )

    print("Creating PowerPoint...")

    ppt_path = create_ppt(
        summary,
        analysis,
        charts,
        insights
    )

    print(
        f"\nReport generated:\n{ppt_path}"
    )


if __name__ == "__main__":
    main()