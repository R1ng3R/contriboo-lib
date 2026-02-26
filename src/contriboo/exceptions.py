"""Typed exception hierarchy used across contriboo modules."""

class ContribooError(Exception):
    """Base exception for contriboo."""


class ContribooConfigurationError(ContribooError):
    """Raised when settings/configuration are invalid."""

    @classmethod
    def invalid_http_timeout(cls) -> "ContribooConfigurationError":
        """Build error for non-positive HTTP timeout setting."""
        return cls("http_timeout_sec must be > 0")

    @classmethod
    def invalid_http_retries(cls) -> "ContribooConfigurationError":
        """Build error for non-positive HTTP retries setting."""
        return cls("http_retries must be > 0")

    @classmethod
    def invalid_http_retry_delay(cls) -> "ContribooConfigurationError":
        """Build error for negative HTTP retry delay setting."""
        return cls("http_retry_delay_sec must be >= 0")

    @classmethod
    def invalid_git_timeout(cls) -> "ContribooConfigurationError":
        """Build error for non-positive git timeout setting."""
        return cls("git_timeout_sec must be > 0")

    @classmethod
    def invalid_max_search_pages(cls) -> "ContribooConfigurationError":
        """Build error for non-positive GitHub search page limit."""
        return cls("max_search_pages must be > 0")


class InvalidDaysRangeError(ContribooError):
    """Raised when days parameter is invalid."""

    @classmethod
    def must_be_positive_or_all(cls) -> "InvalidDaysRangeError":
        """Build error for `days` value outside positive-int/`all` contract."""
        return cls("days must be > 0 or 'all'")

    @classmethod
    def must_be_positive_int_or_all(cls) -> "InvalidDaysRangeError":
        """Build error for `days` with non-int values like bool/str."""
        return cls("days must be positive int or 'all'")


class InvalidRepositoryNameError(ContribooError):
    """Raised when repository full name is invalid."""

    @classmethod
    def invalid_format(cls) -> "InvalidRepositoryNameError":
        """Build error for repository name not matching `owner/repo`."""
        return cls("repository name must be in format 'owner/repo'")

    @classmethod
    def slash_in_part(cls) -> "InvalidRepositoryNameError":
        """Build error for owner/repo segments containing extra slash."""
        return cls("owner and repo must not contain '/'")


class GitHubApiError(ContribooError):
    """Raised for generic GitHub API failures."""

    @classmethod
    def request_failed(cls) -> "GitHubApiError":
        """Build generic GitHub API failure error message."""
        return cls("GitHub API request failed")


class GitHubRateLimitError(GitHubApiError):
    """Raised when GitHub rate limit is exceeded."""

    @classmethod
    def exceeded(cls, wait_seconds: int) -> "GitHubRateLimitError":
        """Build error describing GitHub rate-limit wait duration."""
        message = (
            "GitHub rate limit exceeded. "
            f"Wait about {max(wait_seconds, 0)}s or use token."
        )
        return cls(message)


class GitHubConnectionError(GitHubApiError):
    """Raised for temporary network/DNS issues to GitHub API."""

    @classmethod
    def unreachable(cls) -> "GitHubConnectionError":
        """Build error for persistent DNS/network unreachability."""
        return cls(
            "GitHub API is unreachable (DNS/network issue). "
            "Check internet/VPN/DNS and try again.",
        )


class GitHubResponseSchemaError(GitHubApiError):
    """Raised when GitHub API response has unexpected schema."""

    @classmethod
    def non_object(cls) -> "GitHubResponseSchemaError":
        """Build error for non-object JSON payload from GitHub API."""
        return cls("GitHub API returned non-object response")


class GitOperationError(ContribooError):
    """Raised when git command exits with error."""

    @classmethod
    def empty_command(cls) -> "GitOperationError":
        """Build error for missing git command arguments."""
        return cls("Git command must not be empty")

    @classmethod
    def unsupported_command(cls) -> "GitOperationError":
        """Build error for command lists not starting with `git`."""
        return cls("Only git commands are allowed")


class GitOperationTimeoutError(GitOperationError):
    """Raised when git command times out."""

    @classmethod
    def command_timeout(
        cls,
        timeout_sec: int,
        command: list[str],
    ) -> "GitOperationTimeoutError":
        """Build timeout error with command context for diagnostics."""
        return cls(f"Command timeout after {timeout_sec}s: {' '.join(command)}")
