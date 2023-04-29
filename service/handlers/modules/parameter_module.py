import boto3
from botocore.exceptions import ClientError

from service.handlers.utils.observability import logger, tracer

# Get parameter details from AWS SSM Parameter Store


@tracer.capture_method(capture_response=False)
def get_parameter(parameter_str):
    logger.debug('Function: get_parameter invoked')
    client = boto3.client('ssm')
    try:
        logger.info('Calling AWS System Manager API on get_parameter')
        response = client.get_parameter(
            Name=parameter_str,
            WithDecryption=False
        )
    except ClientError as error:
        if error.response['Error']['Code'] == 'ParameterNotFound':
            # TODO: Reword this
            logger.exception(
                f'Parameter was not found in Parameter Store {str(parameter_str)}')
            raise ValueError(f'A parameter provided was incorrect:\
                              {str(parameter_str)}'
                             .format(error))
        else:
            raise error
    return response

# Split parameter string in a list
# Example string: "/business/application/service/
#                  framework/region/stage/parameter"


def get_parameter_list(parameter_str):
    logger.debug('Function: get_parameter_list invoked')
    list = parameter_str.split("/")
    return list

# Extract the parameter from the end of the string


def get_parameter_key(parameter_list):
    logger.debug('Function: get_parameter_key invoked')
    listlen = (len(parameter_list)-1)
    key = parameter_list[int(listlen)]
    return key
