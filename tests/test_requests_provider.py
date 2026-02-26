from typing import TypedDict, cast

import pytest
import requests

from contriboo.exceptions import GitHubRateLimitError
from contriboo.integrations.github.requests_provider import GitHubProvider

HTTP_ERROR_STATUS_THRESHOLD = 400
EXPECTED_PAGINATED_CALLS = 2


class SessionCall(TypedDict):
    url: str
    headers: dict[str, str]
    params: dict[str, object]
    timeout: int


class FakeResponse:
    def __init__(
        self,
        payload: dict[str, object],
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._payload = payload
        self.status_code = status_code
        self.headers = headers or {}

    def raise_for_status(self) -> None:
        if self.status_code >= HTTP_ERROR_STATUS_THRESHOLD:
            raise requests.HTTPError(response=cast("requests.Response", self))

    def json(self) -> dict[str, object]:
        return self._payload


class FakeSession:
    def __init__(self) -> None:
        self.calls: list[SessionCall] = []

    def get(
        self,
        url: str,
        headers: dict[str, str],
        params: dict[str, object],
        timeout: int,
    ) -> FakeResponse:
        self.calls.append(
            {"url": url, "headers": headers, "params": params, "timeout": timeout},
        )
        page = params["page"]
        if page == 1:
            return FakeResponse(
                {
                    "items": [
                        {"repository": {"full_name": "a/repo1"}},
                        {"repository": {"full_name": "a/repo1"}},
                        {"repository": {"full_name": "b/repo2"}},
                    ],
                },
            )
        return FakeResponse({"items": []})


def test_find_repositories_for_author_deduplicates() -> None:
    session = FakeSession()
    auth_value = f"test-auth-{id(session)}"
    provider = GitHubProvider(
        token=auth_value,
        timeout_sec=30,
        retries=3,
        retry_delay_sec=0,
        max_search_pages=20,
        session=cast("requests.Session", session),
    )

    repositories = provider.find_repositories_for_author(username="octocat", days=10)

    assert sorted(str(repository) for repository in repositories) == [
        "a/repo1",
        "b/repo2",
    ]
    assert repositories[0].owner() in {"a", "b"}
    assert len(session.calls) == EXPECTED_PAGINATED_CALLS
    assert session.calls[0]["headers"]["Authorization"] == f"Bearer {auth_value}"


def test_find_repositories_for_author_supports_all_period() -> None:
    session = FakeSession()
    provider = GitHubProvider(
        token=None,
        timeout_sec=30,
        retries=1,
        retry_delay_sec=0,
        max_search_pages=2,
        session=cast("requests.Session", session),
    )

    provider.find_repositories_for_author(username="octocat", days="all")

    first_params = session.calls[0]["params"]
    query = str(first_params["q"])
    assert query == "author:octocat"
    assert "committer-date" not in query


def test_find_repositories_for_author_handles_rate_limit() -> None:
    class RateSession:
        def get(
            self,
            url: str,
            headers: dict[str, str],
            params: dict[str, object],
            timeout: int,
        ) -> FakeResponse:
            return FakeResponse(
                payload={"message": "rate limit exceeded"},
                status_code=403,
                headers={
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": "9999999999",
                },
            )

    provider = GitHubProvider(
        token=None,
        timeout_sec=30,
        retries=1,
        retry_delay_sec=0,
        max_search_pages=1,
        session=cast("requests.Session", RateSession()),
    )

    with pytest.raises(GitHubRateLimitError) as rate_limit_error:
        provider.find_repositories_for_author(username="octocat", days=1)
    assert "rate limit" in str(rate_limit_error.value).lower()
