import pytest
from httpx import Response

from MoodleClient import AppConfig
from MoodleClient.auth import MoodleTokenAuth, MoodleTokens
from MoodleClient.exceptions import MoodleAuthError, MoodleNetworkError


def test_base_url_matches_app_config(test_config):
    auth = MoodleTokenAuth(http_client=None, app_config=test_config)
    assert auth.base_url == test_config.BASE_URL


def test_generate_app_config_if_missing():
    auth = MoodleTokenAuth(http_client=None)
    assert auth.config is not None
    assert isinstance(auth.config, AppConfig)


def test_token_property_raises_error_when_missing():
    """Ensures accessing the token property raises MoodleAuthError if unauthenticated."""
    auth = MoodleTokenAuth.from_credentials(
        http_client=None, username="user", password="password123"
    )

    with pytest.raises(MoodleAuthError) as exc_info:
        _ = auth.token

    assert "Please authenticate first" in str(exc_info.value)


def test_token_property_returns_correctly():
    token = MoodleTokens(token="tokenabc123", private_token="privatetoken")
    auth = MoodleTokenAuth(http_client=None, token_data=token)

    assert auth.token == "tokenabc123"


def test_from_tokens_creates_configured_instance(mock_http_client, test_config):
    mock_token = "somewebapitoken"
    mock_private_token = "someprivatetoken"
    auth = MoodleTokenAuth.from_tokens(
        http_client=mock_http_client,
        token=mock_token,
        private_token=mock_private_token,
        app_config=test_config,
    )

    assert auth.http == mock_http_client
    assert auth.token_data.token == mock_token
    assert auth.token_data.private_token == mock_private_token
    assert auth.config == test_config


def test_from_credentials_creates_configured_instance(
    mock_http_client, mock_credentials, test_config
):
    mock_username = mock_credentials.username
    mock_password = mock_credentials.password
    auth = MoodleTokenAuth.from_credentials(
        http_client=mock_http_client,
        username=mock_username,
        password=mock_password,
        app_config=test_config,
    )

    assert auth.http == mock_http_client
    assert auth.credentials.username == mock_username
    assert auth.credentials.password == mock_password
    assert auth.config == test_config


async def test_authenticate_without_credentials():
    """authenticate() must raise MoodleAuthError immediately if no credentials were supplied."""
    auth = MoodleTokenAuth(http_client=None)

    with pytest.raises(MoodleAuthError) as exc_info:
        await auth.authenticate()

    assert "No credentials provided" in str(exc_info.value)


async def test_authenticate_success(respx_mock, mock_http_client, mock_credentials, test_config):
    """A 200 response with a token should populate token_data and be returned."""
    route = respx_mock.post(f"{test_config.BASE_URL}/login/token.php").mock(
        return_value=Response(200, json={"token": "abc123", "privatetoken": "priv456"})
    )

    auth = MoodleTokenAuth.from_credentials(
        http_client=mock_http_client,
        username=mock_credentials.username,
        password=mock_credentials.password,
        app_config=test_config,
    )

    result = await auth.authenticate()

    assert route.called
    assert result.token == "abc123"
    assert result.private_token == "priv456"
    # State must actually be mutated on the instance, not just returned
    assert auth.token_data == result
    assert auth.token == "abc123"



async def test_authenticate_success_without_private_token(
    respx_mock, mock_http_client, mock_credentials, test_config
):
    """privatetoken is optional in Moodle's response; missing it should not raise."""
    respx_mock.post(f"{test_config.BASE_URL}/login/token.php").mock(
        return_value=Response(200, json={"token": "abc123"})
    )

    auth = MoodleTokenAuth.from_credentials(
        http_client=mock_http_client,
        username=mock_credentials.username,
        password=mock_credentials.password,
        app_config=test_config,
    )

    result = await auth.authenticate()

    assert result.token == "abc123"
    assert result.private_token is None


async def test_authenticate_missing_token_in_response(
    respx_mock, mock_http_client, mock_credentials, test_config
):
    """Moodle can return 200 with an error payload (e.g. bad login) instead of a token."""
    respx_mock.post(f"{test_config.BASE_URL}/login/token.php").mock(
        return_value=Response(200, json={"error": "Invalid login, please try again"})
    )

    auth = MoodleTokenAuth.from_credentials(
        http_client=mock_http_client,
        username=mock_credentials.username,
        password=mock_credentials.password,
        app_config=test_config,
    )

    with pytest.raises(MoodleAuthError) as exc_info:
        await auth.authenticate()

    assert "missing 'token' key" in str(exc_info.value)
    # Must not silently leave stale/partial token data set
    assert auth.token_data is None


async def test_authenticate_http_status_error(
    respx_mock, mock_http_client, mock_credentials, test_config
):
    """Non-2xx responses should be wrapped as MoodleAuthError with the status code."""
    respx_mock.post(f"{test_config.BASE_URL}/login/token.php").mock(
        return_value=Response(401, json={"error": "invalidlogin"})
    )

    auth = MoodleTokenAuth.from_credentials(
        http_client=mock_http_client,
        username=mock_credentials.username,
        password=mock_credentials.password,
        app_config=test_config,
    )

    with pytest.raises(MoodleAuthError) as exc_info:
        await auth.authenticate()

    assert "HTTP 401" in str(exc_info.value)


async def test_authenticate_network_error(
    respx_mock, mock_http_client, mock_credentials, test_config
):
    """Connection failures should be wrapped as MoodleNetworkError, not leak the raw httpx error."""
    import httpx

    respx_mock.post(f"{test_config.BASE_URL}/login/token.php").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )

    auth = MoodleTokenAuth.from_credentials(
        http_client=mock_http_client,
        username=mock_credentials.username,
        password=mock_credentials.password,
        app_config=test_config,
    )

    with pytest.raises(MoodleNetworkError) as exc_info:
        await auth.authenticate()

    assert "Network error" in str(exc_info.value)


async def test_authenticate_unexpected_error_is_wrapped(
    respx_mock, mock_http_client, mock_credentials, test_config
):
    """Non-JSON/malformed 200 responses should hit the generic except branch, not crash raw."""
    respx_mock.post(f"{test_config.BASE_URL}/login/token.php").mock(
        return_value=Response(200, content=b"not-json-at-all")
    )

    auth = MoodleTokenAuth.from_credentials(
        http_client=mock_http_client,
        username=mock_credentials.username,
        password=mock_credentials.password,
        app_config=test_config,
    )

    with pytest.raises(MoodleAuthError) as exc_info:
        await auth.authenticate()

    assert "Unexpected failure" in str(exc_info.value)


async def test_authenticate_sends_expected_payload(
    respx_mock, mock_http_client, mock_credentials, test_config
):
    """Guards against regressions in the request body Moodle expects."""
    route = respx_mock.post(f"{test_config.BASE_URL}/login/token.php").mock(
        return_value=Response(200, json={"token": "abc123"})
    )

    auth = MoodleTokenAuth.from_credentials(
        http_client=mock_http_client,
        username=mock_credentials.username,
        password=mock_credentials.password,
        app_config=test_config,
    )
    await auth.authenticate()

    sent_request = route.calls.last.request
    sent_body = sent_request.content.decode()
    assert f"username={mock_credentials.username}" in sent_body
    assert f"password={mock_credentials.password}" in sent_body
    assert "service=moodle_mobile_app" in sent_body


async def test_authenticate_overwrites_previous_token(
    respx_mock, mock_http_client, mock_credentials, test_config
):
    """Re-authenticating (e.g. after expiry) should replace the old token, not append/merge."""
    respx_mock.post(f"{test_config.BASE_URL}/login/token.php").mock(
        return_value=Response(200, json={"token": "newtoken"})
    )

    auth = MoodleTokenAuth.from_credentials(
        http_client=mock_http_client,
        username=mock_credentials.username,
        password=mock_credentials.password,
        app_config=test_config,
    )
    auth.token_data = MoodleTokens(token="oldtoken", private_token="oldpriv")

    await auth.authenticate()

    assert auth.token == "newtoken"
    assert auth.token_data.private_token is None
