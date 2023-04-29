from service.handlers.modules import *
from service.handlers.schemas import *
from service.handlers.utils.observability import logger, tracer, metrics
from service.handlers.utils.env_vars_parser import get_environment_variables,\
    init_environment_variables

from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import ValidationError, parse


@logger.inject_lambda_context
@init_environment_variables(model=env_vars.MyHandlerEnvVars)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event: dict, context: LambdaContext) -> str:

    # Getting and Setting Environment and Logging variables
    logger.set_correlation_id(context.aws_request_id)
    valid_env_vars: env_vars.MyHandlerEnvVars = get_environment_variables()
    logger.info(f'AWS ENV Management - \
                {str(valid_env_vars.POWERTOOLS_SERVICE_NAME)}')
    logger.debug('Function: lambda_handler invoked')
    logger.debug('Environment variables', extra=valid_env_vars.dict())

    # Validating event variables

    try:
        logger.debug('Validating event variables')
        parsed_inputs: inputs.Input = parse(event=event, model=inputs.Input)
    except ValidationError as err:
        logger.exception('Unable to parse event variables')
        raise ValueError('Unable to parse event variables')

    # Getting and Setting event input and environment variables
    s3_bucket = valid_env_vars.S3_BUCKET
    messages = parsed_inputs.Messages
    # if 'destination_uris' in parsed_inputs.keys():
    destination_uris = parsed_inputs.destination_uris
    # else:
    #     destination_uris = []
    logger.debug('Event info and Environment variables have been \
                 retrieved and set')

    # Iterating through messages to get prefixes and parameters
    try:
        logger.debug('Trying to starting messages_loop in order to\
                      build prefixes directory')
        prefixes = messages_module.messages_loop(messages)
    except:
        logger.exception('Error encountered during messages_loop')
        raise RuntimeError('Error encountered during messagese_loop')

    # Creating new env file and an updated destination uris list
    try:
        logger.debug('Trying to start prefixes_loop to create new env\
                      files and a updated destination uris list')
        updated_destination_uris = prefixes_module.prefixes_loop(
            prefixes, destination_uris, s3_bucket)
    except:
        logger.exception('Error encountered during prefixes_loop')
        raise RuntimeError('Error encountered during prefixes_loop')

    metrics.add_metric(name="ValidEvents", unit=MetricUnit.Count, value=1)
    logger.info('Valid ENV Management event has been completed')

    return {
        'statusCode': 200,
        'destination_uris': updated_destination_uris
    }
