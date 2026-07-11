from .services import BadgesService, CourseService, WebServiceService
from .session import MoodleSession


class MoodleClient:
    badges: BadgesService
    course: CourseService
    webservice: WebServiceService

    def __init__(self, session: MoodleSession):
        self.badges = BadgesService(session)
        self.course = CourseService(session)
        self.webservice = WebServiceService(session)
