from ..session import MoodleSession


class BaseService:
    def __init__(self, session: MoodleSession):
        self.session = session
