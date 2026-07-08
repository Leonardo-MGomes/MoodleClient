from pydantic import BaseModel

from .common import MoodleDateTime, MoodleWarnings


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
