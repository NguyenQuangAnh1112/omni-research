from typing import Annotated, List, TypedDict

from langchain_core import messages
from langgraph.graph.message import BaseMessage, add_messages


class SuperState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    research_data: List[str]
    current_draft: str
    next_step: str


class ResearcherState(TypedDict):
    topic: str
    logs: Annotated[List[BaseMessage], add_messages]
    findings: List[str]


class WriterState(TypedDict):
    materials: List[str]
    feedback: str
    draft: str
