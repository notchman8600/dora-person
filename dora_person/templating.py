"""Shared Jinja2 template environment.

Kept in its own module so both the routers and the exception handlers in
``main`` render through the exact same template configuration.
"""

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="dora_person/templates")


def get_templates() -> Jinja2Templates:
    return templates
