from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

class ChatBotState(TypedDict):
    is_clear_enough: bool = False
    messages: Annotated[list[AnyMessage], add_messages]
    ingredients: list[str]
    quantities: list[str]
