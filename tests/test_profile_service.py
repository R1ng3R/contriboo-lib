from pathlib import Path
from typing import Any, cast

import pytest

from contriboo.exceptions import GitOperationError, InvalidDaysRangeError
from contriboo.profile.models import CommitSignature
from contriboo.profile.service import ProfileAnalysisService
from contriboo.profile.types import DaysRange
from contriboo.repository_name import RepositoryName

EXPECTED_TOTAL_COMMITS = 2
EXPECTED_REPOS_SCANNED = 3
EXPECTED_REPOS_SKIPPED = 2


class FakeRepositoryProvider:
    def __init__(self, repositories: list[RepositoryName]) -> None:
        self._repositories = repositories

    def find_repositories_for_author(
        self,
        username: str,
        days: DaysRange,
    ) -> list[RepositoryName]:
        return list(self._repositories)


class FakeGitGateway:
    def __init__(self, fail_repository: str | None = None) -> None:
        self._fail_repository = fail_repository

    def clone_repository(
        self,
        repository_full_name: RepositoryName,
        target_root: Path,
    ) -> Path:
        if str(repository_full_name) == self._fail_repository:
            raise GitOperationError
        return target_root / str(repository_full_name).replace("/", "__")

    def resolve_mainline_branch(self, repository_dir: Path) -> str | None:
        if repository_dir.name.endswith("repo3"):
            return None
        return "main"

    def iter_commit_signatures(
        self,
        repository_dir: Path,
        branch: str,
    ) -> list[CommitSignature]:
        if repository_dir.name.endswith("repo1"):
            return [
                CommitSignature("john@example.com", "john", "john@example.com", "john"),
                CommitSignature("x@example.com", "octocat", "x@example.com", "octocat"),
            ]
        return [CommitSignature("none@example.com", "none", "none@example.com", "none")]


def test_count_total_commits_returns_structured_result() -> None:
    service = ProfileAnalysisService(
        repository_provider=FakeRepositoryProvider(
            [
                RepositoryName.parse("a/repo1"),
                RepositoryName.parse("a/repo2"),
                RepositoryName.parse("a/repo3"),
            ],
        ),
        git_gateway=FakeGitGateway(fail_repository="a/repo2"),
    )

    result = service.count_total_commits(
        username="octocat",
        email="john@example.com",
        days="all",
        show_progress=False,
    )

    assert result.total_commits == EXPECTED_TOTAL_COMMITS
    assert result.repos_scanned == EXPECTED_REPOS_SCANNED
    assert result.repos_skipped == EXPECTED_REPOS_SKIPPED
    assert len(result.repo_results) == EXPECTED_REPOS_SCANNED


def test_count_total_commits_validates_days() -> None:
    service = ProfileAnalysisService(
        repository_provider=FakeRepositoryProvider([]),
        git_gateway=FakeGitGateway(),
    )

    with pytest.raises(InvalidDaysRangeError) as zero_days_error:
        service.count_total_commits(username="octocat", email=None, days=0)
    assert "days" in str(zero_days_error.value)

    with pytest.raises(InvalidDaysRangeError) as invalid_string_error:
        service.count_total_commits(
            username="octocat",
            email=None,
            days=cast("Any", "week"),
        )
    assert "days" in str(invalid_string_error.value)

    bool_days: Any = True
    with pytest.raises(InvalidDaysRangeError) as bool_days_error:
        service.count_total_commits(
            username="octocat",
            email=None,
            days=bool_days,
        )
    assert "days" in str(bool_days_error.value)
