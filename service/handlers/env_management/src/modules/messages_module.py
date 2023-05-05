import json

import service.handlers.env_management.src.modules.parameter_module as parameter_module
from service.handlers.utils.observability import logger, metrics
from aws_lambda_powertools.metrics import MetricUnit

# Global variable for PREFIXES dict
PREFIXES = {}

# Get prefix from parameter_str


def get_prefix(parameter_str, parameter_key):
    logger.debug('Function: get_prefix invoked')
    striped_str = parameter_str.lstrip('/')
    prefix = striped_str.rstrip(parameter_key)
    return prefix

# Iterating through messages to get prefixes and parameters


def messages_loop(messages):
    logger.debug('Function: messages_loop invoked')
    global PREFIXES
    for message in messages:
        message_body = json.loads(message['Body'])
        parameter_str = message_body['detail']['name']
        operation = message_body['detail']['operation']

        # Record Parameter request metrics
        if operation == "Create":
            metrics.add_metric(name="CreateParameterRequest",
                               unit=MetricUnit.Count, value=1)
        elif operation == "Update":
            metrics.add_metric(name="UpdateParameterRequest",
                               unit=MetricUnit.Count, value=1)
        elif operation == "Delete":
            metrics.add_metric(name="DeleteParameterRequest",
                               unit=MetricUnit.Count, value=1)
        elif operation == "LabelParameterVersion":
            metrics.add_metric(name="LabelParameterRequest",
                               unit=MetricUnit.Count, value=1)
        else:
            logger.exception(f"Invaild operation provided: {str(operation)}")
            raise ValueError(f"Invaild operation provided: {str(operation)}")

        if operation != 'Delete':
            ssm_response = parameter_module.get_parameter(parameter_str)

        # Getting parameter
        parameter_list = parameter_module.get_parameter_list(parameter_str)
        parameter_key = parameter_module.get_parameter_key(parameter_list)

        # Creating PREFIXES dict
        prefix = get_prefix(parameter_str, parameter_key)
        PREFIXES.setdefault(str(prefix), {})
        key_index = len(PREFIXES[str(prefix)])
        parameter_dict = {
            str(parameter_key): {
                "operation": str(operation),
                "ssm_response": {}
            }
        }
        PREFIXES[str(prefix)][key_index] = parameter_dict

        if operation != 'Delete':
            PREFIXES[str(prefix)][key_index][str(parameter_key)
                                             ]["ssm_response"] = ssm_response
        return PREFIXES
