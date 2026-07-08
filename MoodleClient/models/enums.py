from enum import IntEnum


class BadgeType(IntEnum):
    SITE = 1
    COURSE = 2


class BadgeStatus(IntEnum):
    INACTIVE = 0
    ACTIVE = 1
    INACTIVE_LOCKED = 2
    ACTIVE_LOCKED = 3
    ARCHIVED = 4
