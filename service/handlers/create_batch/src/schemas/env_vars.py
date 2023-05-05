from aws_lambda_powertools.utilities.parser import BaseModel, validator
from pydantic import constr, confloat
from typing import Literal

# Environment Variables validation model


class MyHandlerEnvVars(BaseModel):
    LOG_LEVEL: Literal['DEBUG', 'INFO', 'ERROR', 'CRITICAL',
                       'WARNING', 'EXCEPTION']
    POWERTOOLS_SERVICE_NAME: constr(min_length=1)
    POWERTOOLS_LOGGER_SAMPLE_RATE: confloat(ge=0, le=1)
    POWERTOOLS_TRACE_DISABLED: bool
