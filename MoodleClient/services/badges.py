import logging

from ..models.badges import (
    GetBadgeStructure,
    GetUserBadgeByHashStructure,
    GetUserBadgesStructure,
)
from .base import BaseService, auto_moodle_params

logger = logging.getLogger(__name__)


class BadgesService(BaseService):
    # https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/badges/classes/external/get_badge.php#L47
    # MOODLE_502_STABLE execute_parameters
    @auto_moodle_params
    async def get_badge(self, id: int, data: dict | None = None) -> GetBadgeStructure:
        logger.info(f"Fetching Badge with id: {id}")
        response = await self.session.request(
            "core_badges_get_badge", extra_params=data
        )
        return self._parse_response(response, GetBadgeStructure)

    # https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/badges/classes/external.php#L56
    # MOODLE_502_STABLE get_user_badges_parameters
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
    ) -> GetUserBadgesStructure:
        logger.info("Fetching user badges...")
        response = await self.session.request(
            "core_badges_get_user_badges", extra_params=data
        )
        return self._parse_response(response, GetUserBadgesStructure)

    # https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/badges/classes/external/get_user_badge_by_hash.php#L49
    # MOODLE_502_STABLE execute_parameters
    @auto_moodle_params
    async def get_user_badge_by_hash(
        self, hash: str, data: dict | None = None
    ) -> GetUserBadgeByHashStructure:
        logger.info(f"Fetching User Badge by hash: {hash}")
        response = await self.session.request(
            "core_badges_get_user_badge_by_hash", extra_params=data
        )
        return self._parse_response(response, GetUserBadgeByHashStructure)
