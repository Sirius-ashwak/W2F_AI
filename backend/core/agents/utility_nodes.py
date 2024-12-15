from backend.core.agents.state.chatbot_state import ChatBotState
from typing import Literal
def entry_node(state: ChatBotState):
    pass

def entry_node_output_router(state: ChatBotState) -> Literal["info_gathering_agent", "extract_ingredients_node"]:
    """Router node to determine the next node to route to based on the current state.
    """
    is_clear_enough = state.get('is_clear_enough', False)
    if is_clear_enough:
        return "extract_ingredients_node"
    return "info_gathering_agent"

def ask_human_node(state: ChatBotState):
    pass