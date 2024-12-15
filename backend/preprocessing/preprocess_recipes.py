import pandas as pd
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from backend.core.utils.utils_llm import run_chain_on_inputs
import asyncio
from backend.core.utils.chat_model import ChatVertexAIWX
from loguru import logger
from typing import List
from backend.preprocessing.preprocessing_enums import DifficultyLevel, CookingMethod, Equipment, MealType, CourseType, DietaryRestriction, CleanupEffort

async def extract_title(df_recipes: pd.DataFrame, chat_model: ChatVertexAIWX) -> pd.DataFrame:
    """
    Extracts the title of a recipe from a piece of text.
    
    Args:
        df_recipes: A pandas DataFrame containing the text of recipes.
        chat_model: A ChatVertexAIWX instance.
    
    Returns:
        A pandas DataFrame containing the extracted titles.
    """

    class ExtractedTitle(BaseModel):
        """
        Extracts the title of a recipe from a piece of text.
        """
        title: str = Field(description="The title of the recipe.")


    RECIPE_CHECK_PROMPT = """
    -- Role --
    You are an expert chef and have a deep understanding of recipes and ingredients.

    -- Task --
    Your task is to extract the title of a recipe from a piece of text.

    Extract the title of the recipe from the text.
    Think step by step about the text and the recipe before extracting the title.
    If the title is specified, use that. Otherwise, infer the title from the text.
    A short, descriptive title is preferred.

    -- Input --
    Here is the text containing the recipe:

    {comment_str}
    """ 

    prompt = PromptTemplate(template=RECIPE_CHECK_PROMPT, input_variables=["comment_str"])
    extract_title_chain = prompt | chat_model.with_structured_output(ExtractedTitle)

    title_extract_inputs = []
    for comment in df_recipes['raw_comment']:
        title_extract_inputs.append({
            "comment_str": comment
        })

    results, estimated_cost, _, _ = await run_chain_on_inputs(extract_title_chain, title_extract_inputs, ExtractedTitle)
    logger.info(f"Titles extracted for {len(results)} recipes. Estimated cost: ${estimated_cost} AUD.")

    df_recipes['title'] = [result.title for result in results]
    df_recipes.reset_index(drop=True, inplace=True)

    return df_recipes

async def extract_time(df_recipes: pd.DataFrame, chat_model: ChatVertexAIWX) -> pd.DataFrame:
    """
    Extracts the preparation time of a recipe from a piece of text.
    
    Args:
        df_recipes: A pandas DataFrame containing the text of recipes.
        chat_model: A ChatVertexAIWX instance.
    
    Returns:
        A pandas DataFrame containing the extracted preparation times.
    """

    class ExtractedRecipe(BaseModel):
        """
        Extracts or infers the preparation time of a recipe from a piece of text.
        """
        active_preparation_time: int = Field(description="The total time it takes to actively prepare the recipe, e.g. chopping vegetables, kneading dough, etc. If not specified, estimate it.")
        inactive_preparation_time: int = Field(description="The total time it takes to wait for the recipe, e.g. waiting for the dough to rise, marinating meat, etc. If not specified, estimate it.")
        cooking_time: int = Field(description="The total time it takes to cook the recipe. e.g. baking, boiling, frying, etc. If not specified, estimate it.")


    RECIPE_CHECK_PROMPT = """
    -- Role --
    You are an expert chef that has a deep understanding of recipes and ingredients.
    Your task is to extract or infer the preparation time and cooking time of a recipe from a piece of text.

    -- Task --
    Extract the active preparation time, inactive preparation time, and cooking time of the recipe.
    If the active preparation time is not specified, estimate it. The format should be in minutes.
    If the inactive preparation time is not specified, estimate it. The format should be in minutes.
    If the cooking time is not specified, estimate it. The format should be in minutes.

    -- Input --

    Here is the text containing the recipe:

    {comment_str}
    """ 

    prompt = PromptTemplate(template=RECIPE_CHECK_PROMPT, input_variables=["comment_str"])
    time_extract_chain = prompt | chat_model.with_structured_output(ExtractedRecipe)

    time_extract_inputs = []
    for comment in df_recipes['raw_comment']:
        time_extract_inputs.append({
            "comment_str": comment
        })

    results, estimated_cost, _, _ = await run_chain_on_inputs(time_extract_chain, time_extract_inputs, ExtractedRecipe)
    logger.info(f"Time extracted for {len(results)} recipes. Estimated cost: ${estimated_cost} AUD.")

    df_recipes['active_preparation_time'] = [result.active_preparation_time for result in results]
    df_recipes['inactive_preparation_time'] = [result.inactive_preparation_time for result in results]
    df_recipes['cooking_time'] = [result.cooking_time for result in results]
    df_recipes.reset_index(drop=True, inplace=True)
    
    return df_recipes

async def extract_practical_metadata(df_recipes: pd.DataFrame, chat_model: ChatVertexAIWX) -> pd.DataFrame:
    """
    Extracts the number of servings of a recipe from a piece of text.
    
    Args:
        df_recipes: A pandas DataFrame containing the text of recipes.
        chat_model: A ChatVertexAIWX instance.
    
    Returns:
        A pandas DataFrame containing the extracted recipes.
    """

    class ExtractedPracticalMetadata(BaseModel):
        """
        Extracts the practical metadata of a recipe from a piece of text.
        """
        difficulty_level: DifficultyLevel = Field(description="The difficulty level of the recipe.")
        cooking_method: CookingMethod = Field(description="The primary cooking method of the recipe.")
        equipment: List[Equipment] = Field(description="The equipment needed to make the recipe.")
        cleanup_effort: CleanupEffort = Field(description="The effort required to clean up after the recipe.")

    RECIPE_CHECK_PROMPT = """
    -- Role --
    You are an expert chef and have a deep understanding of recipes and ingredients.
    
    -- Task --
    Your task is to extract the practical metadata of a recipe from a peice of text.

    Extract the difficulty level, primary cooking method, equipment needed, and cleanup effort.
    If the difficulty level is not specified, infer it based on the recipe assuming the target audience is the average home cook, not an expert chef.
    If the primary cooking method is not specified, infer it based on the recipe.
    If the equipment needed is not specified, infer it based on the recipe.
    If the cleanup effort is not specified, infer it based on the recipe.

    Think step by step about the recipe and the ingredients before inferring the practical metadata.

    -- Input --
    Here is the text containing the recipe:

    {comment_str}
    """ 

    prompt = PromptTemplate(template=RECIPE_CHECK_PROMPT, input_variables=["comment_str"])
    practical_metadata_extract_chain = prompt | chat_model.with_structured_output(ExtractedPracticalMetadata)

    practical_metadata_extract_inputs = []
    for comment in df_recipes['raw_comment']:
        practical_metadata_extract_inputs.append({
            "comment_str": comment
        })

    results, estimated_cost, est_input_tokens, est_output_tokens = await run_chain_on_inputs(practical_metadata_extract_chain, practical_metadata_extract_inputs, ExtractedPracticalMetadata)
    logger.info(f"Practical metadata extracted for {len(results)} recipes. Estimated cost: ${estimated_cost} AUD.")

    df_recipes['difficulty_level'] = [result.difficulty_level.value for result in results]
    df_recipes['cooking_method'] = [result.cooking_method.value for result in results]
    df_recipes['equipment'] = [[equipment.value for equipment in result.equipment] for result in results]
    df_recipes['cleanup_effort'] = [result.cleanup_effort.value for result in results]

    df_recipes.reset_index(drop=True, inplace=True)
    return df_recipes


async def extract_cooking_metadata(df_recipes: pd.DataFrame, chat_model: ChatVertexAIWX) -> pd.DataFrame:
    """
    Extracts the cooking metadata of a recipe from a piece of text.
    
    Args:
        df_recipes: A pandas DataFrame containing the text of recipes.
        chat_model: A ChatVertexAIWX instance.
            
    Returns:
        A pandas DataFrame containing the extracted recipes.
    """

    class ExtractedCookingMetadata(BaseModel):
        """
        Extracts the cooking metadata of a recipe from a piece of text.
        """
        servings: int = Field(description="The number of servings the recipe makes.")
        meal_types: List[MealType] = Field(description="Any applicable meal types of the recipe.")
        course_types: List[CourseType] = Field(description="Any applicable course types of the recipe.")
        dietary_restrictions: List[DietaryRestriction] = Field(description="Any dietary restrictions that are OBEYED by the recipe.")


    RECIPE_CHECK_PROMPT = """
    -- Role --
    You are an expert chef and have a deep understanding of recipes and ingredients.
    
    -- Task --
    Your task is to extract the cooking metadata of a recipe from a peice of text.

    Extract the number of servings, any applicable meal types, any applicable course types, and any applicable dietary restrictions.

    If the number of servings is not specified, infer it based on the recipe.
    If the meal types are not specified, infer them based on the recipe.
    If the course types are not specified, infer them based on the recipe.

    If the dietary restrictions that are obeyed by the recipe are not specified, infer them based on the recipe.
    - For example, if the recipe does not contain any meat, it obeys vegetarian but not vegan dietary restrictions.

    Think step by step about the recipe and the ingredients before inferring the cooking metadata.

    -- Input --
    Here is the text containing the recipe:

    {comment_str}
    """ 

    prompt = PromptTemplate(template=RECIPE_CHECK_PROMPT, input_variables=["comment_str"])
    cooking_metadata_extract_chain = prompt | chat_model.with_structured_output(ExtractedCookingMetadata)

    cooking_metadata_extract_inputs = []
    for comment in df_recipes['raw_comment']:
        cooking_metadata_extract_inputs.append({
            "comment_str": comment
        })

    results, estimated_cost, _, _ = await run_chain_on_inputs(cooking_metadata_extract_chain, cooking_metadata_extract_inputs, ExtractedCookingMetadata)
    logger.info(f"Cooking metadata extracted for {len(results)} recipes. Estimated cost: ${estimated_cost} AUD.")

    df_recipes['servings'] = [result.servings for result in results]
    df_recipes['meal_types'] = [[meal_type.value for meal_type in result.meal_types] for result in results]
    df_recipes['course_types'] = [[course_type.value for course_type in result.course_types] for result in results]
    df_recipes['dietary_restrictions'] = [[dietary_restriction.value for dietary_restriction in result.dietary_restrictions] for result in results]
    df_recipes.reset_index(drop=True, inplace=True)
    return df_recipes

async def extract_structure(df_recipes: pd.DataFrame, chat_model: ChatVertexAIWX) -> pd.DataFrame:
    """
    Extracts the structure of a recipe from a piece of text.
    
    Args:
        df_recipes: A pandas DataFrame containing the text of recipes.
        chat_model: A ChatVertexAIWX instance.
            
    Returns:
        A pandas DataFrame containing the extracted recipes.
    """

    class ExtractedStructure(BaseModel):
        """
        Extracts the structure of a recipe from a piece of text.
        """
        ingredient_groups: List[str] = Field(description="The titles of the ingredient groups of the recipe.")
        method_groups: List[str] = Field(description="The titles of the method groups of the recipe.")


    RECIPE_CHECK_PROMPT = """
    -- Role --
    You are an expert chef and have a deep understanding of recipes and ingredients.
    
    -- Task --
    Your task is to extract the ingredient groups and method groups of a recipe from a peice of text.

    Extract the ingredient groups and method groups of the recipe.

    An ingredient group is a group of ingredients that are used together.
    - For example, if the recipe contains a list of ingredients for pasta dough and a list of ingredients for sauce, they should be in different ingredient groups.
    - The titles of the ingredient groups should be descriptive and unique, e.g. "Pasta Dough" and "Sauce".

    A method group is a group of steps in the recipe that are logically connected.
    - For example, if the recipe contains a list of steps for preparing the dough and a list of steps for cooking the sauce, they should be in different method groups.
    - The titles of the method groups should be descriptive and unique, e.g. "Preparing Dough" and "Cooking Sauce".

    Think step by step before extracting the ingredient groups and method groups.

    -- Input --
    Here is the text containing the recipe:

    {comment_str}
    """ 

    prompt = PromptTemplate(template=RECIPE_CHECK_PROMPT, input_variables=["comment_str"])
    structure_extract_chain = prompt | chat_model.with_structured_output(ExtractedStructure)

    structure_extract_inputs = []
    for comment in df_recipes['raw_comment']:
        structure_extract_inputs.append({
            "comment_str": comment
        })

    results, estimated_cost, _, _ = await run_chain_on_inputs(structure_extract_chain, structure_extract_inputs, ExtractedStructure)
    logger.info(f"Structure extracted for {len(results)} recipes. Estimated cost: ${estimated_cost} AUD.")

    df_recipes['ingredient_groups'] = [result.ingredient_groups for result in results]
    df_recipes['method_groups'] = [result.method_groups for result in results]
    df_recipes.reset_index(drop=True, inplace=True)
    return df_recipes


async def extract_instructions(df_recipes: pd.DataFrame, chat_model: ChatVertexAIWX) -> pd.DataFrame:
    """
    Extracts the instructions of a recipe from a piece of text.
    
    Args:
        df_recipes: A pandas DataFrame containing the text of recipes.
        chat_model: A ChatVertexAIWX instance.
            
    Returns:
        A pandas DataFrame containing the extracted recipes.
    """

    class ExtractedInstructions(BaseModel):
        """
        Extracts the instructions of a recipe from a piece of text.
        """
        instructions: List[List[str]] = Field(description="The step by step instructions of the recipe, per method group.")


    RECIPE_CHECK_PROMPT = """
    -- Role --
    You are an expert chef and have a deep understanding of recipes and ingredients.
    
    -- Task --
    Your task is to extract the step by step instructions of a recipe from a peice of text.
    The instructions should be in the order of the method groups.

    Extract the step by step instructions of the recipe, per method group.
    Return the instructions as separate lists in the order of the method groups.

    Think step by step before extracting the instructions.

    -- Input --
    Here is the text containing the recipe:

    {comment_str}

    Here are the titles of the method groups:
    {method_groups}
    """ 

    prompt = PromptTemplate(template=RECIPE_CHECK_PROMPT, input_variables=["comment_str"])
    instructions_extract_chain = prompt | chat_model.with_structured_output(ExtractedInstructions)

    instructions_extract_inputs = []
    for i, comment in enumerate(df_recipes['raw_comment']):
        instructions_extract_inputs.append({
            "comment_str": comment,
            "method_groups": df_recipes['method_groups'].iloc[i]
        })

    results, estimated_cost, _, _ = await run_chain_on_inputs(instructions_extract_chain, instructions_extract_inputs, ExtractedInstructions)
    logger.info(f"Instructions extracted for {len(results)} recipes. Estimated cost: ${estimated_cost} AUD.")

    df_recipes['instructions'] = [result.instructions for result in results]
    df_recipes.reset_index(drop=True, inplace=True)
    return df_recipes

async def extract_ingredients(df_recipes: pd.DataFrame, chat_model: ChatVertexAIWX) -> pd.DataFrame:
    """
    Extracts the ingredients of a recipe from a piece of text.
    
    Args:
        df_recipes: A pandas DataFrame containing the text of recipes.
        chat_model: A ChatVertexAIWX instance.

    Returns:
        A pandas DataFrame containing the extracted recipes.
    """

    class ExtractedIngredients(BaseModel):
        """
        Extracts the ingredients of a recipe from a piece of text.
        """
        ingredient_names: List[List[str]] = Field(description="The ingredients of the recipe, per ingredient group.")
        ingredient_quantities: List[List[str]] = Field(description="The quantities of the ingredients in the recipe, per ingredient group.")


    RECIPE_CHECK_PROMPT = """
    -- Role --
    You are an expert chef and have a deep understanding of recipes and ingredients.
    
    -- Task --
    Your task is to extract the ingredients and their quantities of a recipe from a peice of text.

    Extract the ingredients and their quantities of the recipe, per ingredient group.
    Return the ingredients and their quantities as separate lists in the order of the ingredient groups.

    The unit of the quantities must be in standard units, e.g. grams, kilograms, liters, cups, teaspoons, tablespoons, etc.

    Think step by step before extracting the ingredients and their quantities.
    
    -- Input --
    Here is the text containing the recipe:
    {comment_str}

    Here are the titles of the ingredient groups:
    {ingredient_groups}
    """ 

    prompt = PromptTemplate(template=RECIPE_CHECK_PROMPT, input_variables=["comment_str"])
    ingredients_extract_chain = prompt | chat_model.with_structured_output(ExtractedIngredients)

    ingredients_extract_inputs = []
    for i, comment in enumerate(df_recipes['raw_comment']):
        ingredients_extract_inputs.append({
            "comment_str": comment,
            "ingredient_groups": df_recipes['ingredient_groups'].iloc[i]
        })

    results, estimated_cost, _, _ = await run_chain_on_inputs(ingredients_extract_chain, ingredients_extract_inputs, ExtractedIngredients)
    logger.info(f"Ingredients extracted for {len(results)} recipes. Estimated cost: ${estimated_cost} AUD.")

    df_recipes['ingredient_names'] = [result.ingredient_names for result in results]
    df_recipes['ingredient_quantities'] = [result.ingredient_quantities for result in results]
    df_recipes.reset_index(drop=True, inplace=True)
    return df_recipes


async def extract_search_description(df_recipes: pd.DataFrame, chat_model: ChatVertexAIWX) -> pd.DataFrame:
    """
    Extracts the search description of a recipe from a piece of text.
    
    Args:
        df_recipes: A pandas DataFrame containing the text of recipes.
        chat_model: A ChatVertexAIWX instance.
            
    Returns:
        A pandas DataFrame containing the extracted recipe search descriptions.
    """

    class ExtractedSearchDescription(BaseModel):
        """
        Extracts the search description of a recipe from a piece of text.
        """
        search_description: str = Field(description="The description of the recipe, optimized for search and discovery purposes.")


    RECIPE_SEARCH_DESCRIPTION_PROMPT = """
    -- Role --
    You are an expert chef and have a deep understanding of recipes and ingredients.
    
    -- Task --
    Your task is to prepare a description of a recipe from a peice of text that is optimized for search and discovery purposes.

    - Format Instructions:
        - The description should be a single paragraph.
        - Each sentence should be fully formed and unambiguous, utilizing the title of the recipe instead of generic terms such as "this recipe", or "dish".
        - The first sentence should be a short, descriptive sentence about the recipe.
        - The rest of the paragraph should be a detailed description of the recipe, including the ingredients, cooking method, and any other relevant information.
            - Pay particular attention to including the ingredients used in the recipe.

    - Example:
        - Title: "Classic Spaghetti Carbonara"
        - Description: "This classic spaghetti carbonara recipe is a delicious and easy-to-make dish that is sure to impress your family and friends. The classic spaghetti carbonara has a delicious creamy and cheesy sauce that is made with a combination of eggs, parmesan cheese, and bacon, and is served over spaghetti. The classic spaghetti carbonara is then topped with a generous amount of parmesan cheese and black pepper. This classic spaghetti carbonara recipe is a classic Italian dish that is sure to become a family favorite."

    Think step by step before extracting or generating the description.

    -- Input --
    Here is the text containing the recipe:

    {comment_str}

    Here is the title of the recipe:

    {title}
    """ 

    prompt = PromptTemplate(template=RECIPE_SEARCH_DESCRIPTION_PROMPT, input_variables=["comment_str"])
    search_description_extract_chain = prompt | chat_model.with_structured_output(ExtractedSearchDescription)

    search_description_extract_inputs = []
    for i, comment in enumerate(df_recipes['raw_comment']):
        search_description_extract_inputs.append({
            "comment_str": comment,
            "title": df_recipes['title'].iloc[i]
        })

    results, estimated_cost, _, _ = await run_chain_on_inputs(search_description_extract_chain, search_description_extract_inputs, ExtractedSearchDescription)
    logger.info(f"Search description extracted for {len(results)} recipes. Estimated cost: ${estimated_cost} AUD.")

    df_recipes['search_description'] = [result.search_description for result in results]
    df_recipes.reset_index(drop=True, inplace=True)
    return df_recipes

async def extract_display_description(df_recipes: pd.DataFrame, chat_model: ChatVertexAIWX) -> pd.DataFrame:
    """
    Extracts the display description of a recipe from a piece of text.
    
    Args:
        df_recipes: A pandas DataFrame containing the text of recipes.
        chat_model: A ChatVertexAIWX instance.
            
    Returns:
        A pandas DataFrame containing the extracted recipe display descriptions.
    """

    class ExtractedDisplayDescription(BaseModel):
        """
        Extracts the display description of a recipe from a piece of text.
        """
        display_description: str = Field(description="The description of the recipe, optimized for display purposes.")


    RECIPE_DISPLAY_DESCRIPTION_PROMPT = """
    -- Role --
    You are an expert chef and have a deep understanding of recipes and ingredients.
    
    -- Task --
    Your task is to prepare a description of a recipe from a piece of text that is optimized for display purposes.

    - Format Instructions:
        - The description should be formatted in Markdown, with headings and subheadings.
        - Start with a short, descriptive sentence about the recipe.
        - Then, describe the recipe in detail with the following format:
            - Ingredients: List the ingredients used in the recipe.
                - Use bullet points to list the ingredients, grouped by ingredient group.
            - Cooking Method: Describe the cooking method used in the recipe.
                - Use numbered steps to describe the cooking method, grouped by method group.
            - Additional Information: Include any other relevant information about the recipe.

    Think step by step before extracting or generating the description.

    -- Input --
    Here is the text containing the recipe:

    {comment_str}

    Here is the title of the recipe:

    {title}

    Here are the titles of the ingredient groups:
    {ingredient_groups}

    Here are the titles of the method groups:
    {method_groups}
    """ 

    prompt = PromptTemplate(template=RECIPE_DISPLAY_DESCRIPTION_PROMPT, input_variables=["comment_str"])
    display_description_extract_chain = prompt | chat_model.with_structured_output(ExtractedDisplayDescription)

    display_description_extract_inputs = []
    for i, comment in enumerate(df_recipes['raw_comment']):
        display_description_extract_inputs.append({
            "comment_str": comment,
            "title": df_recipes['title'].iloc[i],
            "ingredient_groups": df_recipes['ingredient_groups'].iloc[i],
            "method_groups": df_recipes['method_groups'].iloc[i]
        })

    results, estimated_cost, _, _ = await run_chain_on_inputs(display_description_extract_chain, display_description_extract_inputs, ExtractedDisplayDescription)
    logger.info(f"Display description extracted for {len(results)} recipes. Estimated cost: ${estimated_cost} AUD.")

    df_recipes['display_description'] = [result.display_description for result in results]
    df_recipes.reset_index(drop=True, inplace=True)
    return df_recipes

async def process_recipes(source: str):
    df_recipes = pd.read_csv(f"backend/data/recipes_{source}_raw.csv")
    chat_model = ChatVertexAIWX(model_name="gemini-1.5-pro-002", project_id=PROJECT_ID, location=LOCATION, temperature=0.5)
    
    # Chain all the async operations
    df_extracted_recipes = await extract_title(df_recipes, chat_model)
    df_extracted_recipes = await extract_time(df_extracted_recipes, chat_model)
    df_extracted_recipes = await extract_practical_metadata(df_extracted_recipes, chat_model)
    df_extracted_recipes = await extract_cooking_metadata(df_extracted_recipes, chat_model)
    df_extracted_recipes = await extract_structure(df_extracted_recipes, chat_model)
    df_extracted_recipes = await extract_instructions(df_extracted_recipes, chat_model)
    df_extracted_recipes = await extract_ingredients(df_extracted_recipes, chat_model)
    df_extracted_recipes = await extract_search_description(df_extracted_recipes, chat_model)
    df_extracted_recipes = await extract_display_description(df_extracted_recipes, chat_model)

    # Create a new column for total time
    df_extracted_recipes['total_time'] = df_extracted_recipes['active_preparation_time'] + df_extracted_recipes['inactive_preparation_time'] + df_extracted_recipes['cooking_time']

    # Unpack ingredient names and quantities into single lists
    df_extracted_recipes['ingredients'] = df_extracted_recipes['ingredient_names'].apply(lambda x: [item for sublist in x for item in sublist])
    df_extracted_recipes['quantities'] = df_extracted_recipes['ingredient_quantities'].apply(lambda x: [item for sublist in x for item in sublist])
    
    # Remove recipes with no instructions or ingredients
    df_extracted_recipes = df_extracted_recipes[[i != [] for i in df_extracted_recipes['instructions']]]
    df_extracted_recipes = df_extracted_recipes[[i != [] for i in df_extracted_recipes['ingredient_names']]]
    logger.info(f"Number of recipes after removing recipes with no instructions or ingredients: {len(df_extracted_recipes)}")
    df_extracted_recipes.to_csv(f"backend/data/recipes_{source}_extracted.csv", index=False)

if __name__ == "__main__":
    asyncio.run(process_recipes("reddit"))