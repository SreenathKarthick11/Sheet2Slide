from langgraph.graph import StateGraph, END

from src.state import Sheet2SlideState
from src.nodes.load_excel import load_excel_node
from src.agents.analysis_agent import analysis_agent
from src.nodes.analysis import analysis_node
from src.agents.visualization_planner import visualization_planner
from src.nodes.generate_charts import generate_charts_node
from src.agents.story_agent import story_agent
from src.nodes.ppt_builder import build_ppt_node


builder = StateGraph(Sheet2SlideState)

builder.add_node("load_excel", load_excel_node)
builder.add_node("analysis_agent", analysis_agent)
builder.add_node("analysis_node", analysis_node)
builder.add_node("visualization_planner", visualization_planner)
builder.add_node("generate_charts", generate_charts_node)
builder.add_node("story_agent", story_agent)
builder.add_node("build_ppt", build_ppt_node)

builder.set_entry_point("load_excel")

builder.add_edge("load_excel", "analysis_agent")
builder.add_edge("analysis_agent", "analysis_node")
builder.add_edge("analysis_node", "visualization_planner")
builder.add_edge("visualization_planner", "generate_charts")
builder.add_edge("generate_charts", "story_agent")
builder.add_edge("story_agent", "build_ppt")
builder.add_edge("build_ppt", END)

graph = builder.compile()