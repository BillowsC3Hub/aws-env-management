from service.handlers.create_batch.src.schemas import *
from service.handlers.utils.observability import logger, tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from service.handlers.utils.env_vars_parser import get_environment_variables,\
    init_environment_variables
from aws_lambda_powertools.utilities.parser import ValidationError, parse


@logger.inject_lambda_context
@init_environment_variables(model=env_vars.MyHandlerEnvVars)
@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event: dict, context: LambdaContext):

    # Getting and Setting Environment and Logging variables
    logger.set_correlation_id(context.aws_request_id)
    valid_env_vars: env_vars.MyHandlerEnvVars = get_environment_variables()
    logger.info(
        f'AWS ENV Management - {str(valid_env_vars.POWERTOOLS_SERVICE_NAME)}')
    logger.debug('Function: lambda_handler invoked')
    logger.debug('Environment variables', extra=valid_env_vars.dict())

    # Validating event variables

    try:
        logger.debug('Validating event variables')
        parsed_inputs: inputs.Input = parse(event=event, model=inputs.Input)
    except ValidationError as err:
        logger.exception('Unable to parse event variables')
        raise ValueError('Unable to parse event variables')

    messages = parsed_inputs.Messages

    batch = []

    for count, value in enumerate(messages):
        batch.append(
            {
                "Id": messages[count]["MessageId"],
                "ReceiptHandle": messages[count]["ReceiptHandle"]
            })

    return {
        'statusCode': 200,
        'body': batch
    }
