import logging
from typing import Any

from httpx import AsyncClient, Response

from .auth import MoodleCredentials, MoodleTokenAuth, MoodleTokens
from .config import DEFAULT_CONFIG, AppConfig

logger = logging.getLogger(__name__)


class MoodleSession:
    def __init__(
        self,
        moodle_auth: MoodleTokenAuth,
        http_client: AsyncClient | None = None,
        app_config: AppConfig | None = None,
    ):
        self.config = app_config or DEFAULT_CONFIG
        self.base_url = self.config.BASE_URL
        self.http = http_client or AsyncClient(
            headers={"User-Agent": self.config.USER_AGENT}
        )
        self.moodle_auth = moodle_auth

    @classmethod
    def from_credentials(
        cls,
        moodle_credentials: MoodleCredentials,
        tokens: MoodleTokens | None = None,
        http_client: AsyncClient | None = None,
        app_config: AppConfig | None = None,
    ) -> "MoodleSession":
        session = cls(moodle_auth=None, http_client=http_client, app_config=app_config)

        moodle_auth = MoodleTokenAuth(
            http_client=session.http,
            moodle_credentials=moodle_credentials,
            token_data=tokens,
        )

        session.moodle_auth = moodle_auth
        return session

    async def request(
        self,
        function: str,
        extra_params: dict[str, Any] | None = None,
        rest_format: str = "json",
    ) -> Response:
        logger.debug(
            f"Calling Moodle API function: {function} with params: {extra_params}"
        )
        data = {
            "wstoken": self.moodle_auth.token,
            "wsfunction": function,
            "moodlewsrestformat": rest_format,
        }
        data.update(extra_params if extra_params else {})

        try:
            response = await self.http.post(
                f"{self.base_url}/webservice/rest/server.php",
                data=data,
            )
            logger.info(f"Moodle API response for {function}: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Moodle API request failed for {function}: {e}")
            raise

    async def close(self):
        await self.http.aclose()
