"""
Shared state object passed between LangGraph nodes.
"""
from typing import TypedDict, Optional, List, Dict, Any
from langchain_core.messages import BaseMessage


class AgentState(TypedDict, total=False):
    # Conversation
    messages: List[BaseMessage]      # running message list (for tool-calling / LangGraph)
    session_id: str
    student_id: Optional[int]

    # Current turn
    query: str
    intent: str                      # "rag" | "tool" | "memory" | "direct"
    student_context: str             # short profile string, e.g. "Dept: CSE; Year: 3"

    # Results
    rag_context: str
    sources: List[Dict[str, Any]]
    tool_output: str
    answer: str
