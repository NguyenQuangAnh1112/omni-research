from typing import Literal

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.agents.researcher import researcher_graph
from src.agents.writer import writer_graph
from src.state import SuperState
from src.tools.file_tools import save_report
from src.utils.logger import logger


def call_researcher(state: SuperState):
    topic = state["messages"][-1].content
    research_input = {"topic": topic, "logs": [], "findings": []}
    result = researcher_graph.invoke(research_input)
    return {"research_data": result["findings"], "next_step": "WRITE"}


def call_writer(state: SuperState):
    writer_input = {
        "materials": state["research_data"],
        "feedback": state["feedback"],
        "draft": "",
    }
    result = writer_graph.invoke(writer_input)
    return {"current_draft": result["draft"], "next_step": "REVIEW"}


def call_publisher(state: SuperState):
    content = state["current_draft"]

    topic = state["messages"][-1].content
    filename = f"report_{topic[:20].strip()}.md"

    result = save_report.invoke({"content": content, "filename": filename})

    return {
        "messages": [HumanMessage(content=f"Đã xong! {result}")],
        "next_step": "FINISH",
    }


def human_review_node(state: SuperState):
    """
    Node này chỉ là một checkpoint để dừng và chờ human review.
    Nó không làm gì cả, chỉ pass state qua.
    """
    logger.info("⏸️  Đang chờ Human Review...")
    return {}


def post_review_router(
    state: SuperState,
) -> Literal["publisher", "end"]:
    """Router sau khi human review - quyết định publish hay kết thúc."""
    step = state.get("next_step", "REVIEW")

    if step == "PUBLISH":
        return "publisher"
    else:
        # REVIEW hoặc FINISH đều kết thúc
        return "end"


workflow = StateGraph(SuperState)

workflow.add_node("researcher", call_researcher)
workflow.add_node("writer", call_writer)
workflow.add_node("human_review", human_review_node)
workflow.add_node("publisher", call_publisher)

# Flow: START → researcher → writer → human_review → (router) → publisher/end
workflow.add_edge(START, "researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", "human_review")

# Sau human_review, dùng router để quyết định
workflow.add_conditional_edges(
    "human_review",
    post_review_router,
    {
        "publisher": "publisher",
        "end": END,
    },
)

workflow.add_edge("publisher", END)

checkpoint = MemorySaver()

# Compile với interrupt TRƯỚC human_review node
# Điều này cho phép graph dừng lại trước khi chạy human_review,
# chờ user update state (PUBLISH/FINISH), rồi mới tiếp tục
app = workflow.compile(checkpointer=checkpoint, interrupt_before=["human_review"])
