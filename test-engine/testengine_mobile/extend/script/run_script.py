from typing import Any


def exec_script(script_code: str, context: dict[str, Any], caseinfo: dict[str, Any] | None = None) -> None:
    from ...core.globalContext import g_context

    exec_globals: dict[str, Any] = {
        "g_context": g_context,
        "caseinfo": caseinfo if caseinfo is not None else {},
        "__builtins__": __builtins__,
    }
    exec_globals.update(context)

    exec(script_code, exec_globals)
