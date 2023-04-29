import os
from typing import Any, TypeVar
from aws_lambda_powertools.utilities.parser import BaseModel, ValidationError

from aws_lambda_powertools.middleware_factory import lambda_handler_decorator


Model = TypeVar("Model", bound=BaseModel)

# global instance of the parsed Pydantic data class
ENV_CONF: BaseModel = None


@lambda_handler_decorator
def init_environment_variables(handler, event, context, model: Model) -> Any:
    global ENV_CONF
    try:
        # parse the os environment variables dict
        ENV_CONF = model(**os.environ)
    except (ValidationError, TypeError) as exc:
        raise ValueError(
            f'failed to load environment variables, exception={str(exc)}'
        ) from exc
    return handler(event, context)


def get_environment_variables() -> BaseModel:
    global ENV_CONF
    if ENV_CONF is None:
        raise ValueError(
            'get_environment_variables was called before '
            'init_environment_variables, environment variables were not loaded'
        )
    return ENV_CONF
