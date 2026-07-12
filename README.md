# MoodleClient

A minimal Python client for interacting with the Moodle Web Services API.

## What this does (and why it exists)

This is a library written to make talking to Moodle way easier. Instead of spending hours reverse-engineering their
endpoints you can just use this.

Under the hood, it uses the **Moodle Mobile API** and registers just like the official app to grab your token.

### One Quick Requirement

Because it acts like the mobile app, you need to make sure **"Web services for mobile devices"** is actually enabled on
the Moodle site you are targeting.

---

## Usage

This library is fully async, so you will need `asyncio` to run it.

### Settings & Environment Variables

You can configure things inside `config.py`. You can either edit the file directly or set these as environment variables
on your system:

| Name           | Environment Variable | Description                       |
|----------------|----------------------|-----------------------------------|
| **Base URL**   | `MOODLE_BASE_URL`    | The URL of your Moodle Instance   |
| **User Agent** | `MOODLE_USER_AGENT`  | The User-Agent sent with Requests |

> **Heads up on the User-Agent**: It's highly recommended to leave this alone. If your Moodle administrator has
> specifically blocked this library's default user-agent, it means they don't want this tool accessing their instance.
> Please respect that and don't just change the user-agent to bypass their block unless you have explicit permission
> from them to use this library.

---

## A Few Important Heads-Up / Disclaimers

* **Mind the Rate Limits:** Moodle servers can be sensitive. Be careful not to loop requests too fast in your scripts,
  or you might trigger security flags and accidentally get your IP or student account temporarily locked out.
* **Use at Your Own Risk:** This is a hobby side-project! If you're using this to automate anything critical (like
  tracking deadlines), remember that Moodle updates can break things. Don't miss a class assignment because a script
  failed.
* **Not Official:** This project is completely unofficial and is not affiliated with Moodle Pty Ltd.

---

### Quick Start / Sample Code

```python
import asyncio
from MoodleClient import MoodleClient, MoodleCredentials, MoodleSession


async def main():
    # Set up your login info and get a session going
    session = MoodleSession.from_credentials(
        MoodleCredentials(username="student", password="securepassword")
    )
    await session.moodle_auth.authenticate()
    client = MoodleClient(session)

    # Fetch data using the built-in services
    # (Available under client.services or the main Client class)
    badges_response = await client.badges.get_user_badges(user_id=4)

    # Everything returned is a validated Pydantic Model for easy typing!
    # (Models are under MoodleClient.models)
    print(badges_response.badges[0])


if __name__ == "__main__":
    # Run the main function with async
    asyncio.run(main())
```

## Contributing & Developer Guide

I'm completely open to contributions! However, to keep the codebase clean, maintainable, and predictable, please follow
these guidelines and coding standards.

### Coding Standards & Naming Conventions

Before opening a Pull Request, make sure your code aligns with these rules:

* **Strict Type Hinting:** All service function arguments and return types must be fully type-hinted. Use highly
  specific custom types where applicable (e.g., `MoodleDateTime`, `TextFormat`, `HttpUrl`) instead of generic strings or
  integers. For complex input arguments, utilize `typing.TypedDict`.
* **Parameter Matching:** Service method parameters must match Moodle's API parameters as closely as possible to
  keep the wrapper predictable.
* **Asynchronous First:** All network-bound operations must use `async`/`await`. Never use synchronous operations (
  `time.sleep()`, synchronous `requests`, etc.).
* **Data Validation via Pydantic:** Do not return raw dictionaries or JSON. Every API response must be parsed into a
  validated **Pydantic Model** (or `RootModel`).
* **The `common.py` Rule:** Any Pydantic model or component that appears in more than one core Moodle domain module (for
  example: `MoodleFile`, `MoodleWarnings`, `Contact`) **must** live in `models/common.py` to prevent circular imports
  and duplication.
* **Logging:** Always instantiate a standard logger at the top of your service files (
  `logger = logging.getLogger(__name__)`). Log a brief, clear info message at the start of every service call (e.g.,
  `logger.info("Checking course updates...")`) to make debugging easier for users.

---

### Local Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and [ruff](https://docs.astral.sh/ruff/)
for linting. Testing is not yet implemented,
but [pytest](https://docs.pytest.org/en/stable/), [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio)
and [respx](https://github.com/lundberg/respx) would be obvious choices.

Most IDE's have automatic ruff support, so it is recommended that it is enabled.

1. Clone the Project and Install Dependencies

```bash
git clone https://github.com/Leonardo-MGomes/MoodleClient.git
cd MoodleClient
uv sync --all-groups
```

2. Linting and Formatting

Always run `ruff` to auto-fix styling issues and check for errors before committing

```bash
# Format code
uv run ruff format .

# Lint and auto-fix safe errors
uv run ruff check . --fix
```

---

### Developer Guide: How to Add a New Moodle Service

Adding a new feature or endpoint follows a strict 3-step pipeline: **Model Definition** $\rightarrow$ **Service
Implementation** $\rightarrow$ **Facade Registration**.

#### Step 1: Define the Pydantic Response Model

Create a data schema for the expected Moodle JSON response inside the appropriate file in `models/`.

* **The `Structure` Suffix:** The final, outermost model representing the root API response *must* end with the word
  `Structure` (e.g., `CheckUpdatesStructure`, `GetCategoriesStructure`).
* Use `BaseModel` for standard key-value objects, and `RootModel` if Moodle returns an array/list at the root level (
  e.g., `RootModel[list[Category]]`).

```python
# models/feature.py
from pydantic import BaseModel
from .common import MoodleWarnings  # Shared types always come from common.py


class FeatureItem(BaseModel):
    id: int
    name: str


# Root response model ending in "Structure"
class GetFeatureStructure(BaseModel):
    items: list[FeatureItem]
    warnings: list[MoodleWarnings]
```

#### 2. Implement the Service Class

Create or update a class file under `services/`. Your naming conventions must strictly map to Moodle's internal Web
Service naming schema:

* **File & Class Name**: Strip the `core_` prefix. The remaining component names map directly to the service file and
  class (e.g., `core_course` becomes `services/course.py` and `class CourseService`).
* **Method Name**: The method name inside your class represents the rest of the Moodle function string (e.g., calling
  `core_course_check_updates` becomes the `check_updates` method inside `CourseService`).
* **The Source Code Comment**: You **must** include a URL comment pointing directly to a **Stable** branch of Moodle (
  e.g.,
  `MOODLE_502_STABLE`) detailing the exact parameter structure you are copying.

**How `@auto_moodle_params` works**: You do not need to manually construct your payload parameters dictionary. The
decorator
automatically strips parameter underscores, converts `bool` to Moodle's expected integer flags (`1` or `0`), and passes
everything dynamically into the `data` parameter. Always include `data: dict | None = None` at the end of your method
arguments.

```python
# services/course.py
import logging
from models.course import CheckUpdatesStructure
from .base import BaseService, auto_moodle_params

# Always set up standard logging
logger = logging.getLogger(__name__)


# core_course -> CourseService
class CourseService(BaseService):

    # Always include a direct link to a STABLE branch, matching this comment format:
    # https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/course/externallib.php#L3506
    # MOODLE_502_STABLE check_updates_parameters
    @auto_moodle_params
    async def check_updates(  # Maps to core_course_check_updates
            self,
            course_id: int,  # Keep parameters as close to Moodle's as possible!
            data: dict | None = None,  # <- Always include this line at the end (if using @auto_moodle_params)!
    ) -> CheckUpdatesStructure:  # <- Returns a "Structure" model
        logger.info("Checking course updates...")

        response = await self.session.request(
            "core_course_check_updates", extra_params=data
        )
        return self._parse_response(response, CheckUpdatesStructure)
```

#### Step 3: Register it on the Client Facade

1. **Expose it in `services/__init__.py`:**
   To make the new service accessible to the rest of the application, it must be exposed through the package
   initialization file. The client Service automatically registers and loads Services that follow convention.

```python
# services/__init__.py
from .course import CourseService
 ```

2.**Add type hinting to the Client (`client.py`):** Add it as a property on the main `MoodleClient` class for better
type hinting.

```python
# client.py
from . import services
from .services.base import BaseService
from .session import MoodleSession


class MoodleClient:
    badges: BadgesService
    course: CourseService  # <- Your new Service here

# Other code
```

### Getting Started with Changes

1. **Open an Issue**: Drop a quick issue describing what endpoint or fix you want to work on so we don't duplicate
   effort.

2. **Submit a PR**: Open a Pull Request targeting the development branch. Ensure your branch name is structured (e.g.,
   `feature/add-course-services`).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
