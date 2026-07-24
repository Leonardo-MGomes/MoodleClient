import asyncio
import logging
from typing import Any, Self

from httpx import AsyncClient, HTTPStatusError, RequestError, Response

from .auth import MoodleCredentials, MoodleTokenAuth, MoodleTokens
from .config import DEFAULT_CONFIG, AppConfig
from .exceptions import MoodleApiError, MoodleNetworkError

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

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

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
            app_config=app_config,
        )

        session.moodle_auth = moodle_auth
        return session

    def _flatten_params(
        self, params: dict[str, Any], parent_key: str = ""
    ) -> dict[str, Any]:
        flat: dict[str, Any] = {}

        for key, value in params.items():
            full_key = f"{parent_key}[{key}]" if parent_key else key

            if isinstance(value, dict):
                flat.update(self._flatten_params(value, full_key))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    indexed_key = f"{full_key}[{i}]"
                    if isinstance(item, (dict, list)):
                        flat.update(self._flatten_params(item, indexed_key))
                    else:
                        flat[indexed_key] = item
            else:
                flat[full_key] = value

        return flat

    async def request(
        self,
        function: str,
        extra_params: dict[str, Any] | None = None,
        rest_format: str = "json",
        max_retries: int = 3,
    ) -> Response:
        logger.debug(
            f"Calling Moodle API function: {function} with params: {extra_params}"
        )
        data = {
            "wstoken": self.moodle_auth.token,
            "wsfunction": function,
            "moodlewsrestformat": rest_format,
        }
        data.update(self._flatten_params(extra_params) if extra_params else {})

        for attempt in range(max_retries):
            try:
                response = await self.http.post(
                    f"{self.base_url}/webservice/rest/server.php",
                    data=data,
                )
                response.raise_for_status()
                logger.debug(
                    f"Moodle API response for {function}: {response.status_code}"
                )
                # TODO: Make this robust
                # This is just so it's caught safely with a Custom error, might need to make it more robust though
                if "exception" in response.json():
                    content = response.json()
                    raise MoodleApiError(
                        content["message"], response.status_code, content
                    )
                return response

            except RequestError as e:
                # Handle timeouts and connection errors
                if attempt == max_retries - 1:
                    logger.error(
                        f"Moodle API request failed after {max_retries} attempts: {e}"
                    )
                    raise MoodleNetworkError(
                        f"Network error occurred while calling {function}: {e}"
                    ) from e

                wait_time = 2**attempt
                logger.warning(
                    f"Network error on attempt {attempt + 1}. Retrying in {wait_time}s... Error: {e}"
                )
                await asyncio.sleep(wait_time)

            except HTTPStatusError as e:
                # Only retry on transient server errors (502, 503, 504)
                if (
                    e.response.status_code in (502, 503, 504)
                    and attempt < max_retries - 1
                ):
                    wait_time = 2**attempt
                    logger.warning(
                        f"Server error {e.response.status_code} on attempt {attempt + 1}. Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                    continue

                logger.error(
                    f"Moodle API returned HTTP {e.response.status_code} for {function}"
                )
                raise MoodleApiError(
                    message=f"Moodle API returned HTTP {e.response.status_code} for {function}",
                    status_code=e.response.status_code,
                    response_body=e.response.text,
                ) from e

            except Exception as e:
                # Catch-all for unexpected errors to ensure they are at least logged and wrapped
                logger.error(
                    f"Unexpected error during Moodle API request for {function}: {e}"
                )
                raise

    async def close(self):
        await self.http.aclose()
