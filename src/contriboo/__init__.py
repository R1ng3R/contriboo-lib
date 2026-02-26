"""Contriboo public package API."""

from .client import ContribooClient
from .exceptions import (
    ContribooConfigurationError,
    ContribooError,
    GitHubApiError,
    GitHubConnectionError,
    GitHubRateLimitError,
    GitHubResponseSchemaError,
    GitOperationError,
    GitOperationTimeoutError,
    InvalidDaysRangeError,
    InvalidRepositoryNameError,
)
from .profile.models import ProfileCommitCountResult, RepositoryCommitCount
from .profile.types import DaysRange
from .repository_name import RepositoryName
from .settings import ContribooSettings

__version__ = "0.1.0"

__all__ = [
    "ContribooClient",
    "ContribooConfigurationError",
    "ContribooError",
    "ContribooSettings",
    "DaysRange",
    "GitHubApiError",
    "GitHubConnectionError",
    "GitHubRateLimitError",
    "GitHubResponseSchemaError",
    "GitOperationError",
    "GitOperationTimeoutError",
    "InvalidDaysRangeError",
    "InvalidRepositoryNameError",
    "ProfileCommitCountResult",
    "RepositoryCommitCount",
    "RepositoryName",
]
