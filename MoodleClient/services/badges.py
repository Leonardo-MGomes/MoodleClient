import logging

from ..models.badges import BadgeStructure
from .base import BaseService, auto_moodle_params

logger = logging.getLogger(__name__)


class BadgesService(BaseService):
    @auto_moodle_params
    async def get_user_badges(
        self,
        user_id: int | None = None,
        course_id: int | None = None,
        page: int | None = None,
        per_page: int | None = None,
        search: str | None = None,
        only_public: bool | None = None,
        data: dict | None = None,
    ) -> BadgeStructure:
        logger.info("Fetching user badges...")
        response = await self.session.request(
            "core_badges_get_user_badges", extra_params=data
        )
        return self._parse_response(response, BadgeStructure)
