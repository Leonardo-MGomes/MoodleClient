from pydantic import BaseModel


# TODO: I currently do not have access to Badges and therefore can not implement them. PR's welcome.
class Badge(BaseModel):
    pass


class BadgeResponse(BaseModel):
    badges: list[dict]
    warnings: list[dict]
