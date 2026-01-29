from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from src.model.llm import llm
from src.state import ResearcherState
from src.tools.search_tools import tavily_tool
from src.utils.exception import he
from src.utils.logger import logger

tools = [tavily_tool]
llm_with_tool = llm.bind_tools(tools)

SYSTEM_PROMPT = """
Bạn là một Chuyên gia Nghiên cứu (Researcher).
Nhiệm vụ: Tìm kiếm thông tin chi tiết, chính xác về chủ đề được giao.
Quy tắc:
1. Sử dụng công cụ tìm kiếm (Tavily) để lấy dữ liệu thực tế.
2. Nếu thông tin chưa đủ, hãy tìm kiếm thêm ở các khía cạnh khác.
3. Khi đã đủ thông tin, hãy đưa ra câu trả lời tổng hợp cuối cùng.
"""


@he
def research_node(state: ResearcherState):
    messages = state["logs"]

    if not messages:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Hãy nghiên cứu về chủ đề: {state['topic']}"),
        ]
    response = llm_with_tool.invoke(messages)

    return {"logs": [response]}


def should_continue(state: ResearcherState):
    last_msg = state["logs"][-1]

    if last_msg.tool_calls:
        logger.info(f"Researcher quyết định dùng Tool: {last_msg.tool_calls}")
        return "tools"
    logger.info("Researcher đã tìm xong thông tin.")
    return "finalize"


@he
def finalize_node(state: ResearcherState):
    last_msg = state["logs"][-1]
    content = last_msg.content
    return {"findings": [str(content)]}


workflow = StateGraph(ResearcherState)
workflow.add_node("agent", research_node)
workflow.add_node("tools", ToolNode(tools, messages_key="logs"))
workflow.add_node("finalize", finalize_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent", should_continue, {"tools": "tools", "finalize": "finalize"}
)

workflow.add_edge("tools", "agent")

workflow.add_edge("finalize", END)

researcher_graph = workflow.compile()
