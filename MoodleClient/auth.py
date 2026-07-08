import logging
from dataclasses import dataclass

from httpx import AsyncClient, HTTPStatusError, RequestError

from MoodleClient.config import DEFAULT_CONFIG, AppConfig
from MoodleClient.exceptions import MoodleAuthError, MoodleNetworkError

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
            raise MoodleAuthError(
                "No Moodle token is available. Please authenticate first."
            )
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
            raise MoodleAuthError("No credentials provided for authentication.")

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

            token = response_content.get("token")
            private_token = response_content.get("privatetoken")

            if not token:
                logger.error(
                    f"Moodle authentication response missing 'token' key: {response_content}"
                )
                raise MoodleAuthError(
                    f"Moodle authentication response missing 'token' key: {response_content}"
                )

            token_data = MoodleTokens(
                token=token,
                private_token=private_token,
            )

            self.token_data = token_data
            logger.info("Successfully authenticated with Moodle.")
            return token_data

        except HTTPStatusError as e:
            logger.error(
                f"Authentication failed with HTTP {e.response.status_code}: {e}"
            )
            raise MoodleAuthError(
                f"Moodle authentication failed with HTTP {e.response.status_code}"
            ) from e
        except RequestError as e:
            logger.error(f"Network error during authentication: {e}")
            raise MoodleNetworkError(f"Network error during authentication: {e}") from e
        except MoodleAuthError:
            raise
        except Exception as e:
            logger.error(f"Unexpected failure during authentication: {e}")
            raise MoodleAuthError(
                f"Unexpected failure during authentication: {e}"
            ) from e
