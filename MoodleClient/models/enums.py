from enum import IntEnum, StrEnum


class BadgeType(IntEnum):
    SITE = 1
    COURSE = 2


class BadgeStatus(IntEnum):
    INACTIVE = 0
    ACTIVE = 1
    INACTIVE_LOCKED = 2
    ACTIVE_LOCKED = 3
    ARCHIVED = 4


class TextFormat(IntEnum):
    MOODLE = 0
    HTML = 1
    PLAIN = 2
    MARKDOWN = 4


class CategoryCriteriaKey(StrEnum):
    ID = "id"
    IDS = "ids"
    NAME = "name"
    PARENT = "parent"
    IDNUMBER = "idnumber"
    VISIBLE = "visible"
    THEME = "theme"


class Homepage(IntEnum):
    SITE_HOME = 0
    DASHBOARD = 1
