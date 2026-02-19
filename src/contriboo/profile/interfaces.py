from pathlib import Path
from typing import Iterable, Protocol

from .models import CommitSignature


class ProfileRepositoryProvider(Protocol):
    def find_repositories_for_author(self, username: str, days: int) -> list[str]:
        ...


class GitHistoryGateway(Protocol):
    def clone_repository(self, repository_full_name: str, target_root: Path) -> Path:
        ...

    def resolve_mainline_branch(self, repository_dir: Path) -> str | None:
        ...

    def iter_commit_signatures(self, repository_dir: Path, branch: str) -> Iterable[CommitSignature]:
        ...
