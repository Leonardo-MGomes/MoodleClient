import logging
from json import JSONDecodeError
from typing import Type, TypeVar

from httpx import Response
from pydantic import ValidationError

from ..exceptions import MoodleValidationError
from ..session import MoodleSession

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseService:
    def __init__(self, session: MoodleSession):
        self.session = session

    @staticmethod
    def _parse_response(response: Response, model: Type[T]) -> T:
        try:
            logger.debug("Attempting API data parsing to JSON...")
            data = response.json()
        except JSONDecodeError as e:
            raise MoodleValidationError(
                f"Failed to decode JSON response for model {model.__name__}: {e}"
            ) from e

        try:
            logger.debug(f"Validating response against model {model.__name__}")
            return model.model_validate(data)
        except ValidationError as e:
            logger.error(f"Failed to validate against model {model.__name__}")
            raise MoodleValidationError(
                f"Failed to validate response against model {model.__name__}: {e}"
            ) from e
        except Exception as e:
            # Not our fault
            logger.error(
                f"Unexpected error validating against model {model.__name__}: {e}"
            )
            raise MoodleValidationError(
                f"Unexpected error validating response against model {model.__name__}: {e}"
            ) from e
