"""
Wrapper for Reddit API.
Using a wrapper simplifies accessing the API, mostly due to handling OAuth.
"""

from enum import Enum, auto
from time import time_ns
from typing import Any

from httpx import BasicAuth, get, post

"""Type of all returning submissions"""
Submission = dict[str, Any]


class SortType(Enum):
    """Enum with all viable sorting types"""

    hot = auto()
    top = auto()
    new = auto()
    controversial = auto()


class RedditApiWrapper:
    """Class wrapping Reddit API

    Class wrapping calls to Reddit API.
    Handles all necessary URLs, parameters, headers, etc.
    Also handles requesting new OAuth 2.0 access tokens and authorization in general.

    Args:
        client_id (str): Reddit app client ID to use for authorization
        client_secret (str): Reddit app client secret to use for authorization
        user_agent (str): user agent used in all Reddit API requests
    """

    _ACCESS_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
    _SUBREDDIT_SUBMISSIONS_URL = "https://oauth.reddit.com/r/{subreddit}/{sort}"
    _USER_SUBMISSIONS_URL = "https://oauth.reddit.com/user/{user}/submitted"
    _AUTH_EXPIRY_OVERHEAD_SECONDS = 60

    def __init__(self, client_id: str, client_secret: str, user_agent: str) -> None:
        self._client_auth = BasicAuth(username=client_id, password=client_secret)
        self._auth_headers = {"User-agent": user_agent}
        self._access_token_expires_in = 0

    async def _authorize(self) -> None:
        response = post(
            url=self._ACCESS_TOKEN_URL,
            params={"grant_type": "client_credentials"},
            auth=self._client_auth,
            headers=self._auth_headers,
        )
        assert response.status_code == 200
        response_content = response.json()
        access_token = response_content["access_token"]
        self._auth_headers["Authorization"] = f"Bearer {access_token}"
        expires_in = response_content["expires_in"]
        self._access_token_expires_in = time_ns() + expires_in - self._AUTH_EXPIRY_OVERHEAD_SECONDS

    async def subreddit_submissions(
        self, subreddit: str, limit: int, sort: SortType
    ) -> list[Submission]:
        """Get a list of Reddit submissions from the given subreddit

        Args:
            subreddit (str): subreddit to load submissions from
            limit (int): up to how many submissions should be loaded
            sort (SortType): sort type to use when loading submissions

        Returns:
            list[Submission]: list of loaded submissions from the given subreddit
        """
        url = self._SUBREDDIT_SUBMISSIONS_URL.format(subreddit=subreddit, sort=sort.name)
        params = {"limit": limit}
        return await self._get_submissions(url, params)

    async def user_submissions(self, user: str, limit: int, sort: SortType) -> list[Submission]:
        """Get a list of Reddit submissions from the given Reddit user

        Args:
            user (str): Reddit user to load submissions from
            limit (int): up to how many submissions should be loaded
            sort (SortType): sort type to use when loading submissions

        Returns:
            list[Submission]: list of loaded submissions from the Reddit user
        """
        url = self._USER_SUBMISSIONS_URL.format(user=user)
        params = {"limit": limit, "sort": sort.name}
        return await self._get_submissions(url, params)

    async def _get_submissions(self, url: str, params: dict[str, Any]) -> list[Submission]:
        if self._access_token_expires_in <= time_ns():
            await self._authorize()
        response = get(url, params=params, headers=self._auth_headers)
        if response.status_code in [401, 403]:
            await self._authorize()
            response = get(url, params=params, headers=self._auth_headers)
        assert response.status_code == 200
        return [submission["data"] for submission in response.json()["data"]["children"]]
