from .services import BadgesService, CourseService
from .session import MoodleSession


class MoodleClient:
    badges: BadgesService
    course: CourseService

    def __init__(self, session: MoodleSession):
        self.badges = BadgesService(session)
        self.course = CourseService(session)
