from os import getenv
from random import randint

from dotenv import load_dotenv
from praw import Reddit
from praw.models import Submission

load_dotenv()
_REDDIT_CLIENT_ID = getenv("REDDIT_CLIENT_ID")
_REDDIT_CLIENT_SECRET = getenv("REDDIT_CLIENT_SECRET")
_REDDIT_CLIENT_USER_AGENT = getenv("REDDIT_CLIENT_USER_AGENT")

_client = Reddit(
    client_id=_REDDIT_CLIENT_ID,
    client_secret=_REDDIT_CLIENT_SECRET,
    user_agent=_REDDIT_CLIENT_USER_AGENT,
)


def get_random_post(subreddit: str, load_count: int = 100) -> Submission:
    random_post_index = randint(1, load_count)
    posts = _client.subreddit(subreddit).hot(limit=random_post_index)
    *_, picked_post = posts
    return picked_post
