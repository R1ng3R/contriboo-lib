import datetime
import tempfile
from pathlib import Path

from .interfaces import GitHistoryGateway, ProfileRepositoryProvider
from .models import ProfileCommitCountResult, RepositoryCommitCount


class ProfileAnalysisService:
    __slots__ = ("__repository_provider", "__git_gateway", "__workspace_dir")

    def __init__(
        self,
        repository_provider: ProfileRepositoryProvider,
        git_gateway: GitHistoryGateway,
        workspace_dir: Path | None = None,
    ) -> None:
        self.__repository_provider = repository_provider
        self.__git_gateway = git_gateway
        self.__workspace_dir = workspace_dir

    def count_total_commits(
        self,
        username: str,
        email: str | None,
        days: int,
        show_progress: bool = False,
    ) -> ProfileCommitCountResult:
        if days <= 0:
            raise ValueError("days must be > 0")

        started_at = datetime.datetime.now(datetime.UTC)
        repositories = self.__repository_provider.find_repositories_for_author(username=username, days=days)
        if not repositories:
            finished_at = datetime.datetime.now(datetime.UTC)
            return ProfileCommitCountResult(
                total_commits=0,
                repos_scanned=0,
                repos_skipped=0,
                started_at=started_at,
                finished_at=finished_at,
                repo_results=(),
            )

        normalized_username = username.strip().lower()
        normalized_email = (email or "").strip().lower()

        total_commits = 0
        repos_skipped = 0
        repo_results: list[RepositoryCommitCount] = []

        with tempfile.TemporaryDirectory(prefix="contriboo-", dir=self.__workspace_dir) as tmp_dir:
            target_root = Path(tmp_dir)
            for index, full_name in enumerate(repositories, start=1):
                if show_progress:
                    print(f"[{index}/{len(repositories)}] cloning {full_name} ...")

                try:
                    repo_dir = self.__git_gateway.clone_repository(full_name, target_root)
                    branch = self.__git_gateway.resolve_mainline_branch(repo_dir)
                    if branch is None:
                        repos_skipped += 1
                        repo_results.append(
                            RepositoryCommitCount(
                                full_name=full_name,
                                branch=None,
                                commit_count=0,
                                status="skipped",
                                error="main/master branch not found",
                            )
                        )
                        if show_progress:
                            print(f"[{index}/{len(repositories)}] skip {full_name}: no main/master")
                        continue

                    repo_commit_count = 0
                    for signature in self.__git_gateway.iter_commit_signatures(repo_dir, branch):
                        if normalized_email and (
                            signature.author_email == normalized_email
                            or signature.committer_email == normalized_email
                        ):
                            repo_commit_count += 1
                            continue
                        if normalized_username and (
                            signature.author_name == normalized_username
                            or signature.committer_name == normalized_username
                        ):
                            repo_commit_count += 1

                    total_commits += repo_commit_count
                    repo_results.append(
                        RepositoryCommitCount(
                            full_name=full_name,
                            branch=branch,
                            commit_count=repo_commit_count,
                            status="ok",
                        )
                    )
                    if show_progress:
                        print(f"[{index}/{len(repositories)}] {full_name}: +{repo_commit_count}")
                except Exception as exc:  # noqa: BLE001
                    repos_skipped += 1
                    repo_results.append(
                        RepositoryCommitCount(
                            full_name=full_name,
                            branch=None,
                            commit_count=0,
                            status="skipped",
                            error=str(exc),
                        )
                    )
                    if show_progress:
                        print(f"[{index}/{len(repositories)}] skip {full_name}: {exc}")

        finished_at = datetime.datetime.now(datetime.UTC)
        return ProfileCommitCountResult(
            total_commits=total_commits,
            repos_scanned=len(repositories),
            repos_skipped=repos_skipped,
            started_at=started_at,
            finished_at=finished_at,
            repo_results=tuple(repo_results),
        )
