import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    BASE_URL: str
    USER_AGENT: str


def create_config() -> AppConfig:
    base_url = os.getenv("MOODLE_BASE_URL", "https://school.moodledemo.net")
    user_agent = os.getenv("MOODLE_USER_AGENT", "moodle-downloader/0.1a4")

    return AppConfig(BASE_URL=base_url, USER_AGENT=user_agent)


DEFAULT_CONFIG = create_config()
