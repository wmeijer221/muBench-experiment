from os import getenv


class MissingEnvironmentVariableError(ValueError):
    """Custom error for a missing environment variable"""
    
    def __init__(self, variable_name: str, **kwargs: object) -> None:
        message = f"Missing variable name: {variable_name}."
        super().__init__(message, **kwargs)


def getenv_non_null(key: str) -> object:
    """Loads a mandatory environment variable."""
    value = getenv(key, None)
    if value is None:
        raise MissingEnvironmentVariableError(key)
    return value
