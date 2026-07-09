from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, StringConstraints


def handle_moodle_zero(value):
    return None if value == 0 else value


MoodleDateTime = Annotated[datetime | None, BeforeValidator(handle_moodle_zero)]
HashStr = Annotated[str, StringConstraints(pattern=r"^[a-fA-F0-9]+$")]


# https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/lib/external/classes/external_warnings.php#L26
# MOODLE_502_STABLE external_warnings
# This extends from 'external_multiple_structure' and thus is ALWAYS inside a list
class MoodleWarnings(BaseModel):
    """Warnings from the Moodle API. Attention, this Model must ALWAYS be inside a list"""

    item: str | None = None
    itemid: int | None = None
    warningcode: str
    message: str
