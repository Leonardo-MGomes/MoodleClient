import logging
from dataclasses import dataclass

from httpx import AsyncClient

from MoodleClient.config import DEFAULT_CONFIG, AppConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MoodleCredentials:
    username: str
    password: str


@dataclass(frozen=True)
class MoodleTokens:
    token: str
    private_token: str | None = None


class MoodleTokenAuth:
    def __init__(
        self,
        http_client: AsyncClient,
        token_data: MoodleTokens | None = None,
        moodle_credentials: MoodleCredentials | None = None,
        app_config: AppConfig | None = None,
    ):
        self.http = http_client
        self.token_data = token_data
        self.credentials = moodle_credentials
        self.config = app_config or DEFAULT_CONFIG
        self.base_url = self.config.BASE_URL

    @property
    def token(self):
        if self.token_data is None:
            raise Exception("No token available.")
        return self.token_data.token

    @classmethod
    def from_tokens(
        cls,
        http_client: AsyncClient,
        token: str,
        private_token: str | None = None,
        **kwargs,
    ) -> "MoodleTokenAuth":
        return cls(
            http_client=http_client,
            token_data=MoodleTokens(token=token, private_token=private_token),
            **kwargs,
        )

    @classmethod
    def from_credentials(
        cls, http_client: AsyncClient, username: str, password: str, **kwargs
    ) -> "MoodleTokenAuth":
        return cls(
            http_client=http_client,
            moodle_credentials=MoodleCredentials(username=username, password=password),
            **kwargs,
        )

    async def authenticate(self) -> MoodleTokens:
        if self.credentials is None:
            logger.error("No credentials provided for authentication")
            raise Exception("No credentials Provided.")

        logger.info("Attempting to authenticate with Moodle...")
        data = {
            "username": self.credentials.username,
            "password": self.credentials.password,
            "service": "moodle_mobile_app",
        }

        try:
            response = await self.http.post(
                f"{self.base_url}/login/token.php", data=data
            )
            response.raise_for_status()
            response_content = response.json()

            token_data = MoodleTokens(
                token=response_content["token"],
                private_token=response_content["privatetoken"],
            )

            self.token_data = token_data
            logger.info("Successfully authenticated with Moodle.")
            return token_data
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
