from src.graph import graph

result = graph.invoke(
    {
        "excel_path":
            "data/sample.xlsx"
    }
)

print(
    result["ppt_path"]
)