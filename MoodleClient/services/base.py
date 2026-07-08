import logging
from functools import wraps
from inspect import signature
from json import JSONDecodeError
from typing import Any, Callable, Type, TypeVar

from httpx import Response
from pydantic import ValidationError

from ..exceptions import MoodleValidationError
from ..session import MoodleSession

logger = logging.getLogger(__name__)

T = TypeVar("T")


def auto_moodle_params(ignore: Callable[..., Any] | list[str] | None = None):
    """
    Advanced decorator factory that automatically extracts, maps, and filters
    method arguments, while ignoring any parameters specified in 'ignore'.
    """
    if callable(ignore):
        return _make_decorator(ignore=None)(ignore)

    return _make_decorator(ignore=ignore)


def _make_decorator(ignore: list[str] | None = None):
    """Helper function to build the actual decorator logic."""
    ignore_set = {"self", "data", "args", "kwargs"}
    if ignore:
        ignore_set.update(ignore)

    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            sig = signature(func)
            bound_args = sig.bind(self, *args, **kwargs)
            bound_args.apply_defaults()

            payload = {}
            params_to_remove = []

            for param_name, value in bound_args.arguments.items():
                if param_name in ignore_set:
                    continue
                if value is not None:
                    payload[param_name.replace("_", "")] = value
                    params_to_remove.append(param_name)

            for param in params_to_remove:
                del bound_args.arguments[param]
            bound_args.arguments["data"] = payload

            return await func(**bound_args.arguments)

        return wrapper

    return decorator


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
