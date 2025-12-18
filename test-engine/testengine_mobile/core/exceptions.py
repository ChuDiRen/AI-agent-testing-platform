class EngineError(Exception):
    pass


class ParserError(EngineError):
    pass


class CaseNotFoundError(EngineError):
    pass


class KeywordError(EngineError):
    pass


class ContextError(EngineError):
    pass


class DriverError(EngineError):
    pass


__all__ = [
    "EngineError",
    "ParserError",
    "CaseNotFoundError",
    "KeywordError",
    "ContextError",
    "DriverError",
]
