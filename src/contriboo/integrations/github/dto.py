from pydantic import BaseModel, Field


class GitHubRepositoryDTO(BaseModel):
    full_name: str


class GitHubCommitSearchItemDTO(BaseModel):
    repository: GitHubRepositoryDTO | None = None


class GitHubCommitSearchResponseDTO(BaseModel):
    items: list[GitHubCommitSearchItemDTO] = Field(default_factory=list)
