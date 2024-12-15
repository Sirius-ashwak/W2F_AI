import praw
from backend.core.env import REDDIT_USER, REDDIT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD
import itertools
import pandas as pd

reddit = praw.Reddit(
    client_id=REDDIT_USER,
    client_secret=REDDIT_SECRET,
    password=REDDIT_PASSWORD,
    user_agent="testscript",
    username=REDDIT_USERNAME,
)

def get_recipe_posts(reddit_client: praw.Reddit, limit: int = None) -> pd.DataFrame:
    """
    Get all the recipe posts from Reddit.

    Args:
        reddit_client (praw.Reddit): The Reddit client.

    Returns:
        pd.DataFrame: A DataFrame containing the recipe posts.
    """
    # Get all the recipes
    recipe_posts = reddit_client.subreddit("recipes").top(time_filter="all", limit=None)
    posts = set()

    for post in recipe_posts:
        posts.add(("https://www.reddit.com/r/recipes/comments/" + post.id, post.url))
    recipe_posts = reddit.subreddit("recipes").top(time_filter="month", limit=limit)
    for post in recipe_posts:
        posts.add(("https://www.reddit.com/r/recipes/comments/" + post.id, post.url))
    recipe_posts = reddit.subreddit("recipes").top(time_filter="year", limit=limit)
    for post in recipe_posts:
        posts.add(("https://www.reddit.com/r/recipes/comments/" + post.id, post.url))
    recipe_posts = reddit.subreddit("recipes").hot(limit=limit)
    for post in recipe_posts:
        posts.add(("https://www.reddit.com/r/recipes/comments/" + post.id, post.url))

    df_recipes = pd.DataFrame(posts, columns=["post_url", "post_image_url"])
    df_recipes['source'] = "reddit"
    return df_recipes

def get_recipe_from_post(reddit_client: praw.Reddit, post_url: str) -> str:
    """
    Get the recipe from a post.

    Args:
        post_url (str): The URL of the post.

    Returns:
        str: The recipe from the post.
    """
    submission = reddit_client.submission(post_url)
    submission.comment_sort = "old"
    # Get only the first comment from the submission.comments generator
    comments = list(itertools.islice(submission.comments, 1))
    recipe_str = ""
    for comment in comments:
        recipe_str += comment.body
    return recipe_str


if __name__ == "__main__":
    df_recipes = get_recipe_posts(reddit, limit=10)

    recipe_posts = []
    for post_url in df_recipes['post_url']:
        recipe_posts.append(get_recipe_from_post(reddit, post_url.split("/")[-1]))

    df_recipes['raw_comment'] = recipe_posts

    df_recipes.to_csv("backend/data/recipes_reddit_raw.csv", index=False)
