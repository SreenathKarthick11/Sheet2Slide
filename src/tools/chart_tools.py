from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


OUTPUT_DIR = Path("output/charts")


def generate_charts_from_plan(df: pd.DataFrame):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    numeric_cols = list(
        df.select_dtypes(include="number").columns
    )

    chart_paths = []

    if len(df.columns) < 2:
        return chart_paths

    x_axis = df.columns[0]

    for col in numeric_cols:

        plt.figure(figsize=(8, 4))

        plt.plot(df[x_axis], df[col])

        plt.title(f"{col} Trend")
        plt.xlabel(x_axis)
        plt.ylabel(col)

        chart_path = OUTPUT_DIR / f"{col}.png"

        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        chart_paths.append(str(chart_path))

    return chart_paths