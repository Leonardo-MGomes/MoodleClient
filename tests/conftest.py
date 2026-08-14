from httpx import AsyncClient
from pytest_asyncio import fixture

from MoodleClient import AppConfig, MoodleCredentials


@fixture(scope="function")
async def mock_http_client():
    async with AsyncClient() as client:
        yield client


@fixture(scope="function")
async def test_config():
    config = AppConfig(
        BASE_URL="https://moodle.example.com", USER_AGENT="moodleclient/0.1a4"
    )
    yield config


@fixture(scope="function")
async def mock_credentials():
    credentials = MoodleCredentials(username="student1", password="studentpassword")
    return credentials
