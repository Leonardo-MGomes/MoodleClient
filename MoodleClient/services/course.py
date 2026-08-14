import logging
from typing import TypedDict

from ..models.course import (
    CheckUpdatesStructure,
    GetCategoriesStructure,
    GetCoursesStructure,
)
from ..models.enums import CategoryCriteriaKey
from .base import BaseService, auto_moodle_params, moodle_endpoint

logger = logging.getLogger(__name__)


class ToCheckItem(TypedDict):
    contextlevel: str
    id: int
    since: int


class CategoryCriteria(TypedDict):
    key: CategoryCriteriaKey
    value: str | int


class CoursesOptions(TypedDict):
    ids: list[int] | None

class CourseService(BaseService):
    # https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/course/externallib.php#L3506
    # MOODLE_502_STABLE check_updates_parameters
    @auto_moodle_params
    @moodle_endpoint
    async def check_updates(
        self,
        course_id: int,
        to_check: list[ToCheckItem],
        filter: list[str] | None = None,
        data: dict | None = None,
    ) -> CheckUpdatesStructure:
        ...

    # https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/course/externallib.php#L1886
    # MOODLE_502_STABLE get_categories_parameters
    @auto_moodle_params
    @moodle_endpoint
    async def get_categories(
        self,
        criteria: list[CategoryCriteria] | None = None,
        add_subcategories: bool | None = True,
        data: dict | None = None,
    ) -> GetCategoriesStructure:
        ...

    # https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/course/externallib.php#L683
    # MOODLE_502_STABLE get_courses_parameters
    @auto_moodle_params
    @moodle_endpoint
    async def get_courses(
        self,
        options: CoursesOptions | None = None,
        data: dict | None = None,
    ) -> GetCoursesStructure:
        ...