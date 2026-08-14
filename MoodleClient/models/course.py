from pydantic import BaseModel, ConfigDict, RootModel

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


# https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/course/externallib.php#L3600
# MOODLE_502_STABLE check_updates_returns
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


# https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/course/externallib.php#L2165
# MOODLE_502_STABLE get_categories_returns
class GetCategoriesStructure(RootModel[list[Category]]):
    pass

# Belongs to Course
class CourseFormatOptions(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    name: str
    value: str

# Belongs to Course
class CustomField(BaseModel):
    name: str
    shortname: str
    type: str
    valueraw: str
    value: str

# Belongs to GetCoursesStructure
class Course(BaseModel):
    id: int
    shortname: str
    categoryid: int
    categorysortorder: int | None = None
    fullname: str
    displayname: str
    idnumber: str | None = None
    summary: str
    summaryformat: TextFormat
    format: str
    showgrades: bool | None = None
    newsitems: int | None = None
    startdate: MoodleDateTime
    enddate: MoodleDateTime
    numsections: int | None = None # Deprecated, use courseformatoptions
    maxbytes: int | None = None
    showreports: bool | None = None
    visible: bool | None = None
    hiddensections: int | None = None # Deprecated, use courseformatoptions
    groupmode: int | None = None # TODO: possible enum
    groupmodeforce: bool | None = None
    defaultgroupingid: int | None = None
    timecreated: MoodleDateTime | None = None
    timemodified: MoodleDateTime | None = None
    enablecompletion: bool | None = None
    completionnotify: bool | None = None
    lang: str | None = None
    forcetheme: str | None = None
    courseformatoptions: list[CourseFormatOptions] | None = None
    showactivitydates: bool
    showcompletionconditions: bool
    customfields: list[CustomField] | None = None


# https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/course/externallib.php#L820
# MOODLE_502_STABLE get_courses_returns
class GetCoursesStructure(RootModel[list[Course]]):
    pass
