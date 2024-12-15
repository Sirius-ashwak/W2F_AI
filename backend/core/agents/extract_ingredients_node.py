from backend.core.agents.state.chatbot_state import ChatBotState
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from backend.core.env import PROJECT_ID, LOCATION
from langchain_core.messages import trim_messages
from loguru import logger
from typing import List
from pydantic import BaseModel, Field
from backend.core.utils.chat_model import ChatVertexAIWX
from backend.core.utils.utils_llm import run_chain_on_inputs, create_gemini_llm_client

def extract_ingredients_node(messages: List):
    logger.info("Extracting ingredients...")
    class IngredientExtraction(BaseModel):
        ingredients: List[str] = Field(
            description="List of unique names of ingredients seen in the image",
        )
        quantities: List[str] = Field(
            description="List of ingredients quantities, in standard metric units",
        )
        reasoning: str = Field(
            description="Explanation of how ingredients were identified and any assumptions made about quantities"
        )

    system_prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.

    -- Role --
    You are an expert chef assistant that analyzes images of ingredients and food items.

    -- Task --
    You will be provided with images of groups of ingredients, or singular ingredients taken by customers, as well as any clarifying information.
    Your task is to identify ingredients and their approximate quantities from images.
    """

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
    chain = prompt | trimmer | chat_model.with_structured_output(IngredientExtraction)

    # Get the structured output
    response = chain.invoke(messages)
    logger.debug(response)
    return {"ingredients": response.ingredients, "quantities": response.quantities}

async def assess_ingredient_node(messages: List, ingredients: List[str], quantities: List[str]):
    logger.info("Assessing ingredients...")
    class IngredientAssessment(BaseModel):
        ingredient: str = Field(
            description="The name of the ingredient being assessed",
        )
        reasoning: str = Field(
            description="Explanation any decisions made about safety and shelf life"
        )
        is_safe_to_consume: bool = Field(
            description="Whether the ingredient appears safe to consume based on visual inspection",
        )
        remaining_shelf_life: str = Field(
            description="The remaining shelf life of the ingredient under standard storage conditions. Give the number and units of measurement.",
        )

    system_prompt = """Today's date is {date}.

    -- Role --
    You are an expert chef assistant that analyzes images of ingredients and food items.

    -- Task --
    You will be provided with images of groups of ingredients, or singular ingredients taken by customers, as well as any clarifying information.
    Your task is to assess the safety and shelf life of a particular ingredient.

    The ingredient is: {ingredient}, and the quantity is: {quantity}
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    
    chat_model = create_gemini_llm_client(project_id=PROJECT_ID, location=LOCATION, model_name="gemini-1.5-pro-002")
    
    assess_ingredient_chain = prompt | chat_model.with_structured_output(IngredientAssessment)

    assessment_inputs = []
    for ingredient, quantity in zip(ingredients, quantities):
        assessment_inputs.append({
            "messages": messages,
            "date": datetime.now().strftime('%d/%m/%Y'),
            "ingredient": ingredient, 
            "quantity": quantity
        })

    results, estimated_cost, _, _ = await run_chain_on_inputs(assess_ingredient_chain, assessment_inputs, IngredientAssessment)
    logger.info(f"Estimated cost to assess {len(results)} ingredients: ${estimated_cost} AUD.")
    
    assessments = []
    for result in results:
        assessments.append(result)
        logger.debug(result)

    return {"ingredients": ingredients, "quantities": quantities, "assessments": assessments}
