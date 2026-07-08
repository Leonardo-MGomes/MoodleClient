from ..models.badges import BadgeResponse
from .base import BaseService


class BadgesService(BaseService):
    async def get_user_badges(self):
        response = await self.session.request("core_badges_get_user_badges")
        badge_response = BadgeResponse.model_validate(response.json())
        return badge_response
