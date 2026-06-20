import sys
import argparse

from src.graph import graph


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a PowerPoint report from an Excel/CSV file."
    )
    parser.add_argument(
        "excel_path",
        nargs="?",
        default="data/sample.xlsx",
        help="Path to the .xlsx/.xls/.csv file to analyze (default: data/sample.xlsx)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        result = graph.invoke({"excel_path": args.excel_path})
    except RuntimeError as exc:
        # Raised deliberately by load_excel_node for bad/missing input files.
        print(f"Failed to process '{args.excel_path}': {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Unexpected error while generating the report: {exc}", file=sys.stderr)
        sys.exit(1)

    ppt_path = result.get("ppt_path")

    if not ppt_path:
        print("Pipeline completed but no PPT was generated.", file=sys.stderr)
        sys.exit(1)

    print(f"Report generated: {ppt_path}")


if __name__ == "__main__":
    main()