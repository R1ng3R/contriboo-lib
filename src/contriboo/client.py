from contriboo.integrations.git.subprocess_gateway import SubprocessGitHistoryGateway
from contriboo.integrations.github.requests_provider import RequestsGitHubProfileRepositoryProvider
from contriboo.profile.service import ProfileAnalysisService
from contriboo.settings import ContribooSettings


class ContribooClient:
    __slots__ = ("__settings", "__profile_service")

    def __init__(
        self,
        settings: ContribooSettings | None = None,
        profile_service: ProfileAnalysisService | None = None,
    ) -> None:
        self.__settings = settings or ContribooSettings()

        if profile_service is not None:
            self.__profile_service = profile_service
            return

        repository_provider = RequestsGitHubProfileRepositoryProvider(
            token=self.__settings.github_token,
            timeout_sec=self.__settings.http_timeout_sec,
            retries=self.__settings.http_retries,
            retry_delay_sec=self.__settings.http_retry_delay_sec,
            max_search_pages=self.__settings.max_search_pages,
        )
        git_gateway = SubprocessGitHistoryGateway(git_timeout_sec=self.__settings.git_timeout_sec)
        self.__profile_service = ProfileAnalysisService(
            repository_provider=repository_provider,
            git_gateway=git_gateway,
            workspace_dir=self.__settings.workspace_dir,
        )

    @property
    def profile(self) -> ProfileAnalysisService:
        return self.__profile_service
