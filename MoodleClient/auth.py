import logging
import typing
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import parse_qsl, urlencode

from httpx import (
    AsyncClient,
    Auth,
    ByteStream,
    HTTPStatusError,
    Request,
    RequestError,
    Response,
)

from .config import DEFAULT_CONFIG, AppConfig
from .exceptions import MoodleAuthError, MoodleNetworkError

logger = logging.getLogger(__name__)


## Implementations
### Dataclasses
@dataclass(frozen=True)
class Credentials:
    username: str
    password: str


@dataclass(frozen=True)
class MobileToken:
    token: str
    private_token: str | None = None


## Protocols
class TokenObject(Protocol):
    token: str


class AuthProtocol(Protocol):
    async def authenticate(self) -> TokenObject:
        pass


### Classes
class TokenAuth(Auth):
    def __init__(self, auth: AuthProtocol, token: TokenObject | None = None):
        self.auth = auth
        self.tokenObject = token

    def sync_auth_flow(
        self, request: Request
    ) -> typing.Generator[Request, Response, None]:
        raise RuntimeError("This auth object is strictly Async only.")

    # TODO: This does not check whether it is still valid (Moodle returns 200 even on auth-failure)
    async def async_auth_flow(
        self, request: Request
    ) -> AsyncGenerator[Request, Response]:
        if not self.tokenObject:
            self.tokenObject = await self.auth.authenticate()

        await self.inject_token(request)

        yield request

    async def inject_token(self, request: Request) -> Request:
        body_bytes = request.read()

        if body_bytes:
            data = dict(parse_qsl(body_bytes.decode("utf-8")))
            data["wstoken"] = self.tokenObject.token
            new_bytes = urlencode(data).encode("utf-8")

            request.stream = ByteStream(new_bytes)
            request.headers["Content-Length"] = str(len(new_bytes))

        return request


class MobileCredentialAuth:
    def __init__(
        self,
        credentials: Credentials,
        http_client: AsyncClient | None = None,
        app_config: AppConfig | None = None,
    ):
        self._credentials = credentials
        self._client = http_client or AsyncClient()
        self._app_config = app_config or DEFAULT_CONFIG
        self._base_url = self._app_config.BASE_URL

    async def authenticate(self) -> MobileToken:
        logger.info("Attempting to authenticate with Moodle...")
        data = {
            "username": self._credentials.username,
            "password": self._credentials.password,
            "service": "moodle_mobile_app",
        }

        try:
            response = await self._client.post(
                f"{self._base_url}/login/token.php",
                data=data,
                auth=None,
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

            token_data = MobileToken(
                token=token,
                private_token=private_token,
            )

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
