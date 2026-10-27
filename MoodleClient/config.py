import os
from dataclasses import dataclass
from importlib.metadata import metadata

from .exceptions import MoodleError


@dataclass(frozen=True)
class AppConfig:
    BASE_URL: str
    USER_AGENT: str

def create_user_agent(package_name: str) -> str:
    data = metadata(package_name)
    version = data.get("version", "dev")
    contact = data.get("project-url", None)
    if contact is None:
        raise MoodleError("Refusing to continue without contact")
    contact = contact.split(", ")[1]
    return f"{package_name}/{version} (+{contact})"

def create_config() -> AppConfig:
    base_url = os.getenv("MOODLE_BASE_URL", "https://school.moodledemo.net")
    user_agent = os.getenv("MOODLE_USER_AGENT", create_user_agent(__package__))

    return AppConfig(BASE_URL=base_url, USER_AGENT=user_agent)


DEFAULT_CONFIG = create_config()
