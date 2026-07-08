import logging
from typing import TypedDict

from ..models.course import CheckUpdatesStructure
from .base import BaseService, auto_moodle_params

logger = logging.getLogger(__name__)


class ToCheckItem(TypedDict):
    contextlevel: str
    id: int
    since: int


class CourseService(BaseService):
    # https://github.com/moodle/moodle/blob/main/public/course/externallib.php#L3506
    @auto_moodle_params
    async def check_updates(
        self,
        course_id: int,
        to_check: list[ToCheckItem],
        filter: list[str] | None = None,
        data: dict | None = None,
    ) -> CheckUpdatesStructure:
        logger.info("Checking course updates...")
        response = await self.session.request(
            "core_course_check_updates", extra_params=data
        )
        return self._parse_response(response, CheckUpdatesStructure)
