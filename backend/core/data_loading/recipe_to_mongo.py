from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain_google_vertexai import VertexAIEmbeddings
from backend.core.utils.utils_mongodb import get_mongodb_collection
from backend.core.env import MONGODB_ATLAS_CLUSTER_URI, PROJECT_ID, LOCATION, PROCESSED_REDDIT_RECIPE_DATA_PATH, RECIPE_VECTOR_INDEX_NAME, RECIPE_FULLTEXT_SEARCH_INDEX_NAME
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_mongodb.index import create_fulltext_search_index
from langchain_core.documents import Document
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger
from typing import List, Dict
import ast
import uuid

def convert_string_to_list(value):
    if isinstance(value, str):
        # Check if the string looks like a list
        if value.startswith('[') and value.endswith(']'):
            try:
                return ast.literal_eval(value)
            except (ValueError, SyntaxError):
                return value
    return value

def recipe_data_from_csv(csv_path: str, id_seed: str) -> List[Document]:
    """
    Load and process recipe data from CSV into a dict.
    
    Returns:
        List of Document chunks with recipe metadata and descriptions
    """
    logger.info(f"Loading recipe data from {csv_path}")
    df = pd.read_csv(csv_path)
    # Cast the df to a list of dicts
    df['uuid'] = df[id_seed].apply(lambda x: str(uuid.uuid5(uuid.NAMESPACE_DNS, x)))
    recipe_data = df.to_dict(orient="records")

    # Convert the dictionary values
    recipe_data = [{
        key: convert_string_to_list(value)
        for key, value in i.items()
    } for i in recipe_data]

    # Unpack ingredient names and quantities into single lists
    for i in recipe_data:
        i["ingredients"] = [item for sublist in i["ingredient_names"] for item in sublist]
        i["quantities"] = [item for sublist in i["ingredient_quantities"] for item in sublist]

    return recipe_data

def recipe_data_to_documents(recipe_data: List[Dict]) -> List[Document]:
    # Prepare Langchain Document objects
    metadata = [{k: v for k, v in i.items() if k != 'search_description'} for i in recipe_data]
    page_content = [i['search_description'] for i in recipe_data]
    documents = [Document(page_content=content, metadata=metadata) for content, metadata in zip(page_content, metadata)]
    return documents

def recipe_data_to_chunks(documents: List[Document]) -> List[Document]:
    """
    Split the documents into chunks - we keep individual sentences as chunks

    Args:
        documents: List of Document objects

    Returns:
        List of Document objects
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=64, chunk_overlap=0, separators=["\. [A-Z]"], keep_separator=True, is_separator_regex=True)
    chunks = text_splitter.split_documents(documents)
    for i in chunks:
        # Remove the first character if it's a period
        if i.page_content[0] == ".":
            i.page_content = i.page_content[1:].lstrip().rstrip(".")
    logger.info(f"Loaded {len(chunks)} recipe data chunks")
    return chunks

def recipe_data_to_vector_store(csv_path: str, mongodb_uri: str, db_name: str, collection_name: str):
    """
    Load recipe data into MongoDB Atlas Vector Search and create vector and fulltext search indexes.
    
    Args:
        mongodb_uri: MongoDB connection URI
        db_name: Name of the database
        collection_name: Name of the collection
        
    Returns:
        MongoDBAtlasVectorSearch: The configured vector store
    """
    recipe_data = recipe_data_from_csv(csv_path, "raw_comment")
    documents = recipe_data_to_documents(recipe_data)
    #chunks = recipe_data_to_chunks(documents)
    embeddings = VertexAIEmbeddings(model="textembedding-gecko@003", project=PROJECT_ID, location=LOCATION)

    recipe_mongodb_collection = get_mongodb_collection(mongodb_uri, db_name, collection_name)
    # Delete existing data in the collection
    logger.info(f"Deleting existing data in the collection")
    recipe_mongodb_collection.delete_many({})

    # Create the vector store
    vector_store = MongoDBAtlasVectorSearch(
        collection=recipe_mongodb_collection,
        embedding=embeddings,
        index_name=RECIPE_VECTOR_INDEX_NAME,
        relevance_score_fn="cosine",
    )

    logger.info(f"Inserting {len(documents)} recipe data chunks into the vector store")
    # Insert the product data into the vector store
    vector_store.add_documents(documents)
    logger.info(f"Inserted {len(documents)} recipe data chunks into the vector store")

    # Create the index
    # Check if the index already exists
    # Check if index exists by getting list of indexes from collection
    search_indexes = recipe_mongodb_collection.list_search_indexes()
    indexes = recipe_mongodb_collection.list_indexes()
    index_exists_fulltext = any(index['name'] == RECIPE_FULLTEXT_SEARCH_INDEX_NAME for index in search_indexes)
    index_exists_vector = any(index['name'] == RECIPE_VECTOR_INDEX_NAME for index in search_indexes)

    if not index_exists_vector:
        logger.info(f"Creating the vector search index")
        vector_store.create_vector_search_index(dimensions=768, filters = ["servings", 
                                                                           "difficulty_level",
                                                                           "cooking_method",
                                                                           "equipment",
                                                                           "cleanup_effort",
                                                                           "meal_types",
                                                                           "course_types",
                                                                           "dietary_restrictions",
                                                                           "total_time",
                                                                           "ingredients",
                                                                           "quantities"])
        logger.info(f"Vector search index created")

    if not index_exists_fulltext:
        logger.info(f"Creating the fulltext search index")
        # Use helper method to create the search index
        create_fulltext_search_index(
            collection = recipe_mongodb_collection,
            field = "search_description",
            index_name = RECIPE_FULLTEXT_SEARCH_INDEX_NAME
        )
        logger.info(f"Fulltext search index created")

    index_exists_title = any("title" in index['name'] for index in indexes)
    if not index_exists_title:
        _ = recipe_mongodb_collection.create_index("title")
        logger.info("Created index on title")

    index_exists_servings = any("servings" in index['name'] for index in indexes)
    if not index_exists_servings:
        _ = recipe_mongodb_collection.create_index("servings")
        logger.info("Created index on servings")

    index_exists_total_time = any("total_time" in index['name'] for index in indexes)
    if not index_exists_total_time:
        _ = recipe_mongodb_collection.create_index("total_time")
        logger.info("Created index on total_time")
    return vector_store

def recipe_data_to_mongodb(csv_path: str, mongodb_uri: str, db_name: str, collection_name: str):
    """
    Load recipe data into MongoDB and create an index.
    """
    recipe_data = recipe_data_from_csv(csv_path, id_seed = "raw_comment")
    recipe_mongodb_collection = get_mongodb_collection(mongodb_uri, db_name, collection_name)
    # Delete existing data in the collection
    recipe_mongodb_collection.delete_many({})
    _ = recipe_mongodb_collection.insert_many(recipe_data)
    logger.info(f"Inserted {len(recipe_data)} recipe data into MongoDB")

    # Check for index and create if not exists
    indexes = recipe_mongodb_collection.list_indexes()
    index_exists_title = any("title" in index['name'] for index in indexes)
    if not index_exists_title:
        _ = recipe_mongodb_collection.create_index("title")
        logger.info("Created index on title")
    
    logger.info(f"Recipe data loaded to MongoDB")
    return recipe_mongodb_collection

if __name__ == "__main__":
    # _ = recipe_data_to_mongodb(
    #     PROCESSED_REDDIT_RECIPE_DATA_PATH,
    #     MONGODB_ATLAS_CLUSTER_URI,
    #     "savour",
    #     "reddit_recipe_parent_data"
    # )

    _ = recipe_data_to_vector_store(
        PROCESSED_REDDIT_RECIPE_DATA_PATH,
        MONGODB_ATLAS_CLUSTER_URI,
        "savour",
        "reddit_recipe_data"
    )
