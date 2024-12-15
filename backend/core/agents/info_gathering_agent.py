from backend.core.agents.state.chatbot_state import ChatBotState
from langchain_core.messages import AIMessage
from typing import Literal
from langchain_core.runnables.config import RunnableConfig
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from backend.core.env import PROJECT_ID, LOCATION
from langchain_core.messages import trim_messages
from loguru import logger
from pydantic import BaseModel, Field
from backend.core.utils.chat_model import ChatVertexAIWX
import uuid

def info_gathering_agent_output_router(state: ChatBotState) -> Literal["ask_human"]:
    """Router node to determine the next node.
    """
    return "ask_human"

def info_gathering_agent(state: ChatBotState, config: RunnableConfig):
    """Information Gathering Agent"""
    logger.info("Entering Information Gathering Agent")
    
    system_prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.

    -- Role --
    You are an expert chef assistant that analyzes images of ingredients and food items.
    You are Nigella Lawson, the queen of food.
    You have an encyclopedic knowledge of food and all ingredients.

    -- Task --
    You will be provided with images of groups of ingredients, or singular ingredients taken by a customer along with messages from the customer.
    Your task is to determine if you can reasonably identify all ingredients and estimate their quantities from the provided image(s) and message(s).

    -- Instructions --  
    - ONLY ask for SPECIFIC follow-ups on what items or ingredients you cannot reliably identify.
        - Do not ask for an overall confirmation.
        - Do not list all the ingredients you can see to the user. 
    - You only need enough to ESTIMATE quantities, the user will be able to adjust your estimation later.
    - If there are no ingredients visible in the images, tell the user what you can see and ask them to upload a new image.
    - If you do not have all the information you need in the images and messages compose a follow up message that:
        - Thanks the user
        - Asks for specific clarification of the items or ingredients you cannot identify
    - If you have all the information you need in the images and messages compose a follow up message that:
        - Thanks the user for the image or message, depending on what they provided
        - Explains that you will now extract all the ingredients
        - Explain that you will provide a table for them to review
    """

    class ImageQualityCheck(BaseModel):
        """Determines if ingredients can be indentified and quantities estimated from images of ingredients."""
        is_clear_enough: bool = Field(description="Whether the image and messages are clear enough to identify all ingredients and estimate quantities")
        missing_info: str = Field(description="What additional information would be helpful, if any")
        reasoning: str = Field(description="Explanation of why the current information (images and messages) is or isn't sufficient")
        follow_up_message: str = Field(description="A message to send back to the user.")


    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    chat_model = ChatVertexAIWX(model_name="gemini-2.0-flash-exp", project_id=PROJECT_ID, location=LOCATION, temperature=0.5)

    trimmer = trim_messages(
        max_tokens=250,
        strategy="last",
        token_counter=len,
        include_system=True,
    )

    chain = prompt | trimmer | chat_model.with_structured_output(ImageQualityCheck)

    # Get the structured output
    response = chain.invoke({"messages": state['messages']})
    logger.debug(response)

    # Specifically extract the AI response to relay to the user
    formatted_response = AIMessage(content = response.follow_up_message, id=str(uuid.uuid4()))

    # Sets the is_clear_enough bool and appends the response message to the output
    return {"is_clear_enough": response.is_clear_enough, "messages": [formatted_response]}