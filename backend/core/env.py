import os
from dotenv import load_dotenv
from loguru import logger

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
# Use absolute path to ensure .env file is found
from pathlib import Path

root_dir = Path(__file__).parent
env_path = root_dir / "local" / "envs" / f".env.{ENVIRONMENT}"

if env_path.exists():
    logger.info(f"Loaded environment variables from {env_path}")
    load_dotenv(env_path)
else:
    # raise FileNotFoundError(f"Environment file not found at {env_path}")
    logger.warning(f"Environment file not found at {env_path}")

# environment-specific variables
PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ["LOCATION"]
MONGODB_ATLAS_CLUSTER_URI = os.environ["MONGODB_ATLAS_CLUSTER_URI"]

DEFAULT_GOOGLE_MODEL = os.environ.get("DEFAULT_GOOGLE_MODEL", "gemini-1.5-flash")
SERVER_PORT= int(os.environ.get("SERVER_PORT", 8000))

# constants across environments
GEMINI_PRO_FAMILY = "gemini-1.5-pro"
GEMINI_PRO = "gemini-1.5-pro-002"
GEMINI_FLASH_FAMILY = "gemini-1.5-pro"
GEMINI_FLASH = "gemini-1.5-flash-002"

# Data paths
PROCESSED_REDDIT_RECIPE_DATA_PATH = "backend/data/recipes_reddit_extracted.csv"
RECIPE_VECTOR_INDEX_NAME = "recipe_vector_index"
RECIPE_FULLTEXT_SEARCH_INDEX_NAME = "recipe_fulltext_search_index"

# Reddit
REDDIT_USER = os.environ["REDDIT_USER"]
REDDIT_SECRET = os.environ["REDDIT_SECRET"]
REDDIT_USERNAME = os.environ["REDDIT_USERNAME"]
REDDIT_PASSWORD = os.environ["REDDIT_PASSWORD"]

# Langsmith
LANGCHAIN_API_KEY = os.environ["LANGCHAIN_API_KEY"]
LANGCHAIN_ENDPOINT = os.environ["LANGCHAIN_ENDPOINT"]
LANGCHAIN_PROJECT = os.environ["LANGCHAIN_PROJECT"]
