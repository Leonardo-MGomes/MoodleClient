import logging

from ..models.badges import BadgeResponse
from .base import BaseService

logger = logging.getLogger(__name__)


class BadgesService(BaseService):
    async def get_user_badges(self):
        logger.debug("Fetching user badges...")
        response = await self.session.request("core_badges_get_user_badges")
        badge_response = BadgeResponse.model_validate(response.json())
        return badge_response
