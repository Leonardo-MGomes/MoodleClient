from .services import BadgesService
from .session import MoodleSession


class MoodleClient:
    badges: BadgesService

    def __init__(self, session: MoodleSession):
        self.badges = BadgesService(session)
