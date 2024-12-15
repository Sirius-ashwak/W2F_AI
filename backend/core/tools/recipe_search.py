from loguru import logger
from pydantic import BaseModel, Field
from backend.core.env import PROJECT_ID, LOCATION
from backend.core.env import MONGODB_ATLAS_CLUSTER_URI, RECIPE_VECTOR_INDEX_NAME, RECIPE_FULLTEXT_SEARCH_INDEX_NAME
from langchain.prompts import PromptTemplate
from backend.core.utils.utils_llm import run_chain_on_inputs, create_gemini_llm_client
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_mongodb.retrievers.hybrid_search import MongoDBAtlasHybridSearchRetriever
from backend.core.utils.utils_mongodb import get_mongodb_collection
from langchain_google_vertexai import VertexAIEmbeddings
from loguru import logger
from langchain_core.documents import Document
import asyncio

recipe_mongodb_collection = get_mongodb_collection(MONGODB_ATLAS_CLUSTER_URI, "savour", "reddit_recipe_data")

embeddings = VertexAIEmbeddings(model="textembedding-gecko@003", project=PROJECT_ID, location=LOCATION)
vector_store = MongoDBAtlasVectorSearch(
    collection=recipe_mongodb_collection,
    embedding=embeddings,
    index_name=RECIPE_VECTOR_INDEX_NAME,
    relevance_score_fn="cosine",
)

retriever = MongoDBAtlasHybridSearchRetriever(
    vectorstore = vector_store,
    search_index_name = RECIPE_FULLTEXT_SEARCH_INDEX_NAME,
    top_k = 15,
    fulltext_penalty = 50,
    vector_penalty = 50
)


def retrieve_recipes(query:str, 
                     k:int = 10, 
                     servings:int = 0, 
                     max_total_time:int = 0, 
                     ingredients:list[str] = [],
                     meal_types:list[str] = [],
                     course_types:list[str] = [],
                     dietary_restrictions:list[str] = [],
                     difficulty_level:list[str] = []) -> list[Document]:
    """
    Retrieve recipes from the database based on the user's query and filters.
    
    Args:
        query (str): The user's query.
        k (int): The number of recipes to retrieve.
        servings (int): The number of servings the recipe should make.
        max_total_time (int): The maximum total time the recipe should take.
        ingredients (list[str]): The ingredients the user wants to use.
        meal_types (list[str]): The meal types the user wants to use.
        course_types (list[str]): The course types the user wants to use.
        dietary_restrictions (list[str]): The dietary restrictions the user wants to use.
        difficulty_level (list[str]): The difficulty level the user wants to use.

    Returns:
        list[Document]: The recipes that match the user's query and filters.
    """
    retriever.top_k = k
    pre_filter = {}
    if servings:
        pre_filter["servings"] = {"$gt": servings}
    if max_total_time:
        pre_filter["total_time"] = {"$lt": max_total_time}
    if meal_types:
        pre_filter["meal_types"] = {"$in": meal_types}
    if course_types:
        pre_filter["course_types"] = {"$in": course_types} 
    if dietary_restrictions:
        pre_filter["dietary_restrictions"] = {"$in": dietary_restrictions}
    if ingredients:
        pre_filter["ingredient_names"] = {"$in": ingredients}
    if difficulty_level:
        pre_filter["difficulty_level"] = {"$in": difficulty_level}


    retriever.pre_filter = pre_filter

    logger.info(f"Retrieving recipes for query: {query}")
    results = retriever.invoke(query)


    # ====================================================================================
    # Aspect filtering - determine if the product matches the customer query
    # ====================================================================================
    aspect_summary_prompt = """-- Role --
    You are an expert chef working for an online recipe recommendation service.

    -- Task --
    You are given a customer request, and a recipe candidate.
    Your task is to determine whether or not the recipe is a good match for the customer request.

    -- Instructions --
        -is_match: The recipe is a match if it contains ANY of the requested ingredients.
        -match_score: The match score should be calculated (0-100, higher is better) based on the following criteria:
            1. Match on ingredients, ingredient state and ingredient quantity
                - Pay attention to the ingredient state. For example, if the customer requests "tomatoes", and the recipe uses "tomato sauce", this is NOT a good match.
                - If the recipe contains more of the requested ingredients, the match score should be higher.
                    - If the recipe uses MORE of an ingredient than the customer requested, the match score should be lower, since the customer does not have that much of that ingredient.

            2. Match on description
                - The description should be relevant to the customer query.

    Customer query: {query}
    Recipe details: {recipe_candidate}
    """

    prompt = PromptTemplate(template=aspect_summary_prompt, input_variables=["query", "recipe_details"])


    class RecipeMatch(BaseModel):
        reasoning: str = Field(description="A short explanation of your reasoning for the customer to read.")
        is_match: bool = Field(description="Whether or not the product is a match for the customer query. You should return True if any requested ingredients are present in the recipe. If none of the requested ingredients are present, you should return False.")
        match_score: float = Field(description="The score of the match, between 0 and 100, higher is better.")

    model = create_gemini_llm_client(project_id=PROJECT_ID, location=LOCATION, model_name="gemini-1.5-pro-002")
    chain = prompt | model.with_structured_output(RecipeMatch)

    # Prepare the chain inputs
    recipe_candidates = [i.metadata['title'] + "\n\n" + i.page_content + "\n\n" + i.metadata["display_description"] for i in results]
    chain_inputs = [{"query":query, "recipe_candidate":recipe_candidate} for recipe_candidate in recipe_candidates]
    recipe_matches, _, _, _ = asyncio.run(run_chain_on_inputs(chain, chain_inputs, default_model=RecipeMatch))
    # Add reasoning and match_score to results
    for result, recipe_match in zip(results, recipe_matches):
        result.metadata['reasoning'] = recipe_match.reasoning
        result.metadata['match_score'] = recipe_match.match_score
        
    # Create list of tuples with (result, match_score) and sort by score descending
    scored_results = [(result, recipe_match.match_score) for result, recipe_match in zip(results, recipe_matches) if recipe_match.is_match]
    scored_results.sort(key=lambda x: x[1], reverse=True)
    # Extract just the results in sorted order
    recipe_results = [result for result, _ in scored_results]

    return recipe_results