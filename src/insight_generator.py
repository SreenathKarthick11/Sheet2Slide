def generate_insights(analysis: dict):

    insights = []

    for column, stats in analysis.items():

        insight = (
            f"{column}: "
            f"average={stats['mean']}, "
            f"max={stats['max']}, "
            f"min={stats['min']}."
        )

        insights.append(insight)

    return insights