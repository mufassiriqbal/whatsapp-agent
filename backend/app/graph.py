from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.llm import get_llm
from app.prompts import SYSTEM_PROMPT
from app.tools import search_knowledge


def build_graph() -> CompiledStateGraph:
    def agent(state: MessagesState) -> dict[str, list[BaseMessage]]:
        model = get_llm().bind_tools([search_knowledge])
        messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        return {"messages": [model.invoke(messages)]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent)
    builder.add_node("tools", ToolNode([search_knowledge]))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    return builder.compile()


graph = build_graph()