from typing import ClassVar

from . import services
from .services.base import BaseService
from .session import MoodleSession


class MoodleClient:
    badges: services.BadgesService
    course: services.CourseService
    webservice: services.WebServiceService

    _service_classes: ClassVar[dict[str, type[BaseService]]] = {}
    _registry_initialized: bool = False

    def __init__(self, session: MoodleSession):
        self._session = session
        self._instances: dict[str, BaseService] = {}

        MoodleClient._initialize_service_registry()

    @classmethod
    def _initialize_service_registry(cls):
        if cls._registry_initialized:
            return

        for attr_name in dir(services):
            attr = getattr(services, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseService)
                and attr is not BaseService
            ):
                normalized_name = attr_name.lower()
                if normalized_name.endswith("service"):
                    shorthand = normalized_name[:-7]
                    cls._service_classes[shorthand] = attr

        cls._registry_initialized = True

    def __getattr__(self, name: str) -> BaseService:
        requested_name = name.lower()

        if requested_name in self._instances:
            return self._instances[requested_name]

        service_class = self._service_classes.get(requested_name)

        if not service_class:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

        instance = service_class(self._session)
        self._instances[requested_name] = instance

        # Here it is set to `name` instead of `requested_name` because some people might write capitalized and bypass the attribute
        setattr(self, name, instance)

        return instance
