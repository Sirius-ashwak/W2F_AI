from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from backend.core.agents.info_gathering_agent import info_gathering_agent, info_gathering_agent_output_router
from backend.core.agents.utility_nodes import entry_node, entry_node_output_router, ask_human_node
from backend.core.agents.extract_ingredients_node import extract_ingredients_node
from backend.core.agents.state.chatbot_state import ChatBotState

# Define a graph
workflow = StateGraph(ChatBotState)
# Add nodes
workflow.add_node("info_gathering_agent", info_gathering_agent)
workflow.add_node("ask_human", ask_human_node)

# Set the entrypoint as route_query
workflow.set_entry_point("info_gathering_agent")

# Determine graph edges
workflow.add_conditional_edges(
    "info_gathering_agent",
    info_gathering_agent_output_router,
)

# The checkpointer lets the graph persist its state
memory = MemorySaver()
app = workflow.compile(checkpointer=memory, interrupt_before=["ask_human"])