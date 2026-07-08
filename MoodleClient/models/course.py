from pydantic import BaseModel, RootModel

from .common import MoodleDateTime, MoodleWarnings
from .enums import TextFormat


# Belongs to CheckUpdateStructure
class CheckUpdatesUpdates(BaseModel):
    name: str
    timeupdated: MoodleDateTime | None = None
    itemids: list[int] | None = None


# Belongs to CheckUpdateStructure
class CheckUpdatesData(BaseModel):
    contextlevel: str
    id: int
    updates: list[CheckUpdatesUpdates]


# https://github.com/moodle/moodle/blob/main/public/course/externallib.php#L3600
class CheckUpdatesStructure(BaseModel):
    instances: list[CheckUpdatesData]
    warnings: list[MoodleWarnings]


# Belongs to GetCategoriesStructure
class Category(BaseModel):
    id: int
    name: str
    idnumber: str | None = None
    description: str
    descriptionformat: TextFormat
    parent: int
    sortorder: int
    coursecount: int
    visible: bool | None = None
    visibleold: bool | None = None
    timemodified: MoodleDateTime | None = None
    depth: int
    path: str
    theme: str | None = None


# https://github.com/moodle/moodle/blob/main/public/course/externallib.php#L2165
class GetCategoriesStructure(RootModel[list[Category]]):
    pass
