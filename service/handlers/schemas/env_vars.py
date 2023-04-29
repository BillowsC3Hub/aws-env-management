from aws_lambda_powertools.utilities.parser import BaseModel, validator
from pydantic import constr, confloat
from typing import Literal
import re

# Environment Variables validation model


class MyHandlerEnvVars(BaseModel):
    LOG_LEVEL: Literal['DEBUG', 'INFO', 'ERROR', 'CRITICAL',
                       'WARNING', 'EXCEPTION']
    POWERTOOLS_SERVICE_NAME: constr(min_length=1)
    POWERTOOLS_LOGGER_SAMPLE_RATE: confloat(ge=0, le=1)
    POWERTOOLS_METRICS_NAMESPACE: constr(min_length=1)
    POWERTOOLS_TRACE_DISABLED: bool
    S3_BUCKET: constr(min_length=1)

    @validator('POWERTOOLS_METRICS_NAMESPACE', 'POWERTOOLS_SERVICE_NAME')
    def check_AWS_not_at_start(cls, v):
        if re.match(r"^((?!\AAWS/).)*$", v) == None:
            raise ValueError(
                'AWS/ is not allowed at the start of this variable')
        return v

    @validator('POWERTOOLS_METRICS_NAMESPACE', 'POWERTOOLS_SERVICE_NAME')
    def only_ascii_char(cls, v):
        if re.match(r"^[\x20-\x7E]*$", v, re.ASCII) == None:
            raise ValueError(
                'non-ASCII or command characters are not allowed')
        return v

    # Uses same RegEx as destination_uris in input schemas
    @validator('S3_BUCKET')
    def check_object_Key_chars(cls, v):
        if re.match(r"^[\w!\-.*'\(\)/&$@=;:+,? ]*$", v) == None:
            raise ValueError(
                'Char not allowed in AWS S3 Object Key')
        return v
