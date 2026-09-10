"""
LangGraph agent for the AI Student Support Assistant.

Graph shape:

    START -> load_context -> classify_intent
                                  |-- "rag"    --> retrieve_rag --> generate_answer --> END
                                  |-- "tool"   --> tool_agent --(has tool calls)--> tools --> tool_agent (loop)
                                  |                    \\--(no tool calls)--> generate_answer --> END
                                  |-- "memory" --> update_memory --> classify_intent (re-route, memory disallowed)
                                  |-- "direct" --> generate_answer --> END
"""
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from agent.state import AgentState
from agent.tools import ALL_TOOLS
from agent.prompts import ROUTER_SYSTEM_PROMPT, ANSWER_SYSTEM_PROMPT, DIRECT_SYSTEM_PROMPT
from llm.gemma import get_llm
from rag.retriever import retrieve, format_chunks_for_prompt
from memory.memory import (
    extract_profile_facts,
    update_student_profile,
    get_student_context,
)
from logging_config import get_logger

logger = get_logger(__name__)

FALLBACK_MESSAGE = "I couldn't find this information in the available college knowledge base."

_SMALL_TALK_PHRASES = (
    "hi", "hello", "hey", "hii", "hlo", "good morning", "good afternoon",
    "good evening", "thanks", "thank you", "thx", "bye", "goodbye",
    "who are you", "what can you do", "what are you", "how are you",
)


def _is_small_talk(query: str) -> bool:
    """Only treat very short greeting/thanks/meta messages as genuine small talk."""
    q = query.strip().lower().rstrip("!.? ")
    if len(q.split()) > 6:
        return False
    return any(q == p or q.startswith(p) for p in _SMALL_TALK_PHRASES)


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def load_context_node(state: AgentState) -> AgentState:
    """Loads the student's known profile (name/department/year/semester)."""
    context = get_student_context(state.get("student_id"))
    return {"student_context": context}


def classify_intent_node(state: AgentState, allow_memory: bool = True) -> AgentState:
    """Uses the LLM as a lightweight router to decide the next step."""
    llm = get_llm(temperature=0.0)
    options = "rag, tool, memory, direct" if allow_memory else "rag, tool, direct"
    prompt = ROUTER_SYSTEM_PROMPT
    if not allow_memory:
        prompt += f"\n(Note: only choose from: {options})"

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=state["query"]),
    ]
    try:
        response = llm.invoke(messages)
        intent = response.content.strip().lower()
        if intent not in ("rag", "tool", "memory", "direct"):
            intent = "rag"  # safe default for college questions
    except Exception as e:
        logger.error(f"Intent classification failed, defaulting to 'rag': {e}")
        intent = "rag"

    # Safety net: small local models sometimes misclassify real questions as
    # "direct" small talk. Only allow "direct" through for genuine greetings/
    # thanks/meta messages; everything else falls back to RAG so the answer
    # is grounded in the knowledge base instead of invented.
    if intent == "direct" and allow_memory and not _is_small_talk(state["query"]):
        logger.info("Overriding misclassified 'direct' intent to 'rag' (not small talk).")
        intent = "rag"
    elif intent == "direct" and not allow_memory and not _is_small_talk(state["query"]):
        intent = "rag"

    logger.info(f"Classified intent: {intent}")
    return {"intent": intent}


def retrieve_rag_node(state: AgentState) -> AgentState:
    """Runs semantic retrieval against ChromaDB."""
    chunks = retrieve(state["query"])
    context = format_chunks_for_prompt(chunks)
    sources = [{"source": c.source, "page": c.page} for c in chunks]
    return {"rag_context": context, "sources": sources}


def tool_agent_node(state: AgentState) -> AgentState:
    """LLM decides which SQLite-backed tool(s) to call, with arguments."""
    llm = get_llm(temperature=0.0).bind_tools(ALL_TOOLS)

    existing_messages = state.get("messages") or []
    if not existing_messages:
        system = SystemMessage(
            content=(
                "You are a college assistant with access to tools for exam schedules, "
                "syllabus, department info, notices and the academic calendar. "
                f"Student profile: {state.get('student_context', 'unknown')}. "
                "Use the appropriate tool(s) to answer the student's question. "
                "Always pass department codes in uppercase (e.g. CSE)."
            )
        )
        existing_messages = [system, HumanMessage(content=state["query"])]

    response = llm.invoke(existing_messages)
    return {"messages": existing_messages + [response]}


def tools_router(state: AgentState) -> Literal["tools", "generate_answer"]:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and getattr(last_message, "tool_calls", None):
        return "tools"
    return "generate_answer"


def collect_tool_output_node(state: AgentState) -> AgentState:
    """After ToolNode executes, gather the tool outputs into plain text for the final prompt."""
    outputs = []
    for m in state["messages"]:
        if isinstance(m, ToolMessage):
            outputs.append(str(m.content))
    tool_output = "\n\n".join(outputs)
    sources = [{"source": "SQLite Database", "page": "-"}] if tool_output.strip() else []
    return {"tool_output": tool_output, "sources": sources}


def update_memory_node(state: AgentState) -> AgentState:
    """Extracts and persists profile facts mentioned in the user's message."""
    facts = extract_profile_facts(state["query"])
    if facts and state.get("student_id"):
        update_student_profile(state["student_id"], facts)
    updated_context = get_student_context(state.get("student_id"))
    logger.info(f"Memory updated with facts: {facts}")
    return {"student_context": updated_context}


def reclassify_after_memory_node(state: AgentState) -> AgentState:
    """Re-run routing (excluding 'memory') now that the profile has been updated."""
    return classify_intent_node(state, allow_memory=False)


def generate_answer_node(state: AgentState) -> AgentState:
    """Produces the final natural-language answer using whatever context is available."""
    llm = get_llm(temperature=0.3)
    intent = state.get("intent")

    if intent == "direct":
        messages = [
            SystemMessage(content=DIRECT_SYSTEM_PROMPT),
            HumanMessage(content=state["query"]),
        ]
        response = llm.invoke(messages)
        return {"answer": response.content, "sources": []}

    context = state.get("rag_context") or state.get("tool_output") or ""

    if not context.strip() or "NO_RESULTS" in context:
        return {"answer": FALLBACK_MESSAGE, "sources": []}

    system_prompt = ANSWER_SYSTEM_PROMPT.format(
        student_context=state.get("student_context") or "Not known yet.",
        context=context,
    )
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["query"]),
    ]
    response = llm.invoke(messages)
    return {"answer": response.content}


def memory_ack_node(state: AgentState) -> AgentState:
    """If memory update wasn't followed by a real question, acknowledge the stored info."""
    return {
        "answer": f"Got it! I've noted that. ({state.get('student_context', '')})",
        "sources": [],
    }


# ---------------------------------------------------------------------------
# Graph wiring
# ---------------------------------------------------------------------------

def route_after_classify(state: AgentState) -> str:
    intent = state.get("intent")
    if intent == "rag":
        return "retrieve_rag"
    if intent == "tool":
        return "tool_agent"
    if intent == "memory":
        return "update_memory"
    return "generate_answer"  # direct


def route_after_memory(state: AgentState) -> str:
    intent = state.get("intent")
    if intent == "rag":
        return "retrieve_rag"
    if intent == "tool":
        return "tool_agent"
    return "memory_ack"


def build_graph(checkpointer=None):
    graph = StateGraph(AgentState)

    graph.add_node("load_context", load_context_node)
    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("retrieve_rag", retrieve_rag_node)
    graph.add_node("tool_agent", tool_agent_node)
    graph.add_node("tools", ToolNode(ALL_TOOLS))
    graph.add_node("collect_tool_output", collect_tool_output_node)
    graph.add_node("update_memory", update_memory_node)
    graph.add_node("reclassify_after_memory", reclassify_after_memory_node)
    graph.add_node("generate_answer", generate_answer_node)
    graph.add_node("memory_ack", memory_ack_node)

    graph.set_entry_point("load_context")
    graph.add_edge("load_context", "classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_after_classify,
        {
            "retrieve_rag": "retrieve_rag",
            "tool_agent": "tool_agent",
            "update_memory": "update_memory",
            "generate_answer": "generate_answer",
        },
    )

    graph.add_edge("retrieve_rag", "generate_answer")

    graph.add_conditional_edges(
        "tool_agent",
        tools_router,
        {"tools": "tools", "generate_answer": "collect_tool_output"},
    )
    graph.add_edge("tools", "tool_agent")
    graph.add_edge("collect_tool_output", "generate_answer")

    graph.add_edge("update_memory", "reclassify_after_memory")
    graph.add_conditional_edges(
        "reclassify_after_memory",
        route_after_memory,
        {
            "retrieve_rag": "retrieve_rag",
            "tool_agent": "tool_agent",
            "memory_ack": "memory_ack",
        },
    )

    graph.add_edge("generate_answer", END)
    graph.add_edge("memory_ack", END)

    return graph.compile(checkpointer=checkpointer)
