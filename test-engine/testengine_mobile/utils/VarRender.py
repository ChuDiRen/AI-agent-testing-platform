from typing import Any

from jinja2 import Template


def refresh(target: Any | None, context: dict[str, Any]) -> str | None:
    if target is None:
        return None
    return Template(str(target)).render(context)
