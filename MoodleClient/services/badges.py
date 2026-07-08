import logging

from ..models.badges import BadgeResponse
from .base import BaseService

logger = logging.getLogger(__name__)


class BadgesService(BaseService):
    async def get_user_badges(self) -> BadgeResponse:
        logger.info("Fetching user badges...")
        response = await self.session.request("core_badges_get_user_badges")
        return self._parse_response(response, BadgeResponse)
