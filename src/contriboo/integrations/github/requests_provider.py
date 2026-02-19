import datetime
import time

import requests

from contriboo.profile.interfaces import ProfileRepositoryProvider

from .dto import GitHubCommitSearchResponseDTO


class RequestsGitHubProfileRepositoryProvider(ProfileRepositoryProvider):
    __slots__ = (
        "__token",
        "__base_url",
        "__timeout_sec",
        "__retries",
        "__retry_delay_sec",
        "__max_search_pages",
        "__session",
    )

    def __init__(
        self,
        token: str | None,
        timeout_sec: int,
        retries: int,
        retry_delay_sec: int,
        max_search_pages: int,
        session: requests.Session | None = None,
        base_url: str = "https://api.github.com",
    ) -> None:
        self.__token = token
        self.__base_url = base_url.rstrip("/")
        self.__timeout_sec = timeout_sec
        self.__retries = retries
        self.__retry_delay_sec = retry_delay_sec
        self.__max_search_pages = max_search_pages
        self.__session = session or requests.Session()

    def find_repositories_for_author(self, username: str, days: int) -> list[str]:
        since = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=days)).date()
        query = f"author:{username} committer-date:>={since.isoformat()}"

        repositories: dict[str, bool] = {}
        for page in range(1, self.__max_search_pages + 1):
            payload = self.__get_json(
                "/search/commits",
                params={"q": query, "per_page": 100, "page": page},
            )
            dto = GitHubCommitSearchResponseDTO.model_validate(payload)
            if not dto.items:
                break

            for item in dto.items:
                repository = item.repository
                if repository is not None:
                    repositories[repository.full_name] = True

        return list(repositories.keys())

    def __get_json(self, path: str, params: dict[str, object]) -> dict[str, object]:
        url = f"{self.__base_url}{path}"
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.__token:
            headers["Authorization"] = f"Bearer {self.__token}"

        for attempt in range(1, self.__retries + 1):
            try:
                response = self.__session.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=self.__timeout_sec,
                )
                response.raise_for_status()
                raw_json = response.json()
                if not isinstance(raw_json, dict):
                    raise RuntimeError("GitHub API returned non-object response")
                return raw_json
            except requests.HTTPError as exc:
                rate_limit_action = self.__handle_rate_limit(exc)
                if rate_limit_action == "retry":
                    continue
                if isinstance(rate_limit_action, str):
                    raise RuntimeError(rate_limit_action) from exc
                raise
            except (requests.ConnectionError, requests.Timeout) as exc:
                if attempt < self.__retries:
                    time.sleep(self.__retry_delay_sec)
                    continue
                raise RuntimeError(
                    "GitHub API is unreachable (DNS/network issue). "
                    "Check internet/VPN/DNS and try again."
                ) from exc

        raise RuntimeError("GitHub API request failed")

    def __handle_rate_limit(self, exc: requests.HTTPError) -> str | None:
        response = exc.response
        if response is None:
            return None

        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        if response.status_code != 403 or remaining != "0" or reset is None:
            return None

        wait_seconds = int(reset) - int(time.time()) + 1
        if 0 < wait_seconds <= 60:
            time.sleep(wait_seconds)
            return "retry"

        return f"GitHub rate limit exceeded. Wait about {max(wait_seconds, 0)}s or use token."
