from datetime import timedelta
from typing import Literal

from pydantic import BaseModel, EmailStr, HttpUrl

from .common import HashStr, MoodleDateTime, MoodleWarnings
from .enums import BadgeStatus, BadgeType


# https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/badges/classes/external/badgeclass_exporter.php#L39
# MOODLE_502_STABLE badgeclass_exporter
class BadgeClass(BaseModel):
    type: Literal["BadgeClass"] = "BadgeClass"
    id: HttpUrl  # No, this isn't wrong: https://github.com/moodle/moodle/blob/main/public/lib/badgeslib.php#L540
    issuer: str | None = None
    name: str
    image: HttpUrl
    description: str
    hostedUrl: HttpUrl | None = None
    courseid: int | None = None
    coursefullname: str | None = None


# https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/badges/classes/external/get_badge.php#L99
# MOODLE_502_STABLE execute_returns
class GetBadgeStructure(BaseModel):
    badge: BadgeClass
    warnings: list[MoodleWarnings]


# https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/badges/classes/external/user_badge_exporter.php#L43
# MOODLE_502_STABLE user_badge_exporter
class UserBadge(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None
    timecreated: MoodleDateTime = 0
    timemodified: MoodleDateTime = 0
    usercreated: int | None = None
    usermodified: int | None = None
    issuername: str
    issuerurl: HttpUrl
    issuercontact: EmailStr | None = None
    expiredate: MoodleDateTime = None
    expireperiod: timedelta | None = None
    type: BadgeType = 1
    courseid: int | None = None
    coursefullname: str | None = None
    message: str | None = None
    messagesubject: str | None = None
    attachment: bool = 1
    notification: bool = 1
    nextcron: MoodleDateTime = None
    status: BadgeStatus = 0
    issuedid: int | None = None
    uniquehash: HashStr
    dateissued: MoodleDateTime = 0
    dateexpire: MoodleDateTime = None
    visible: bool = 0
    recipientid: int
    recipientfullname: str
    email: EmailStr | None = None
    version: str | None = None
    language: str | None = None
    imagecaption: str | None = None


# https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/badges/classes/external.php#L143
# MOODLE_502_STABLE get_user_badges_returns
class GetUserBadgesStructure(BaseModel):
    badges: list[UserBadge]
    warnings: list[MoodleWarnings]
