import re
from io import StringIO
from dotenv import dotenv_values

from service.handlers.modules import env_file_module
from service.handlers.utils.observability import logger, metrics
from aws_lambda_powertools.metrics import MetricUnit

# Create env json using the .env file


def create_env_json(env_file):
    logger.debug('Function: create_env_json invoked')
    env_str = env_file.decode()
    env_stream = StringIO(env_str)
    env_json = dotenv_values(stream=env_stream)
    return env_json

# Sort .env json by key


def sort_env_json(env_json):
    logger.debug('Function: sort_env_json invoked')
    keys = list(env_json.keys())
    keys.sort()
    sorted_json = {i: env_json[i] for i in keys}
    return sorted_json


# Create .env key labels list


def create_key_labels(sorted_json):
    logger.debug('Function: create_key_labels invoked')
    labels = list(())
    for key in sorted_json:
        m = re.match(r"[a-zA-Z]*", key)
        L = m.group(0)
        x = labels.count(L)
        if x == 0:
            labels.append(L)
    labels.sort()
    return labels

# Creating new env file and an updated destination uris list


def prefixes_loop(prefixes, destination_uris, s3_bucket):
    logger.debug('Function: Prefixes_loop invoked')
    if destination_uris == None:
        destination_uris = []

    for prefix in prefixes:
        # destination_uris is required as part of this
        #   Lambda functions output payload
        while destination_uris.count(prefix) >= 1:
            destination_uris.remove(prefix)
        else:
            destination_uris.append(prefix)

        object_key = prefix + ".env"
        prefix_dict = prefixes[str(prefix)]
        s3_response = env_file_module.get_env_file(s3_bucket, object_key)

        env_json = create_env_json(s3_response)

        logger.debug('Updating .env json')
        for value in prefixes[str(prefix)]:

            for x in prefixes[str(prefix)][value]:
                if prefix_dict[value][str(x)]["operation"] \
                        != 'Delete':
                    env_json[str(x)] = prefix_dict[value][str(
                        x)]["ssm_response"]["Parameter"]["Value"]
                elif prefix_dict[value][str(x)]["operation"] == 'Delete' \
                        and x in env_json.keys():
                    env_json.pop(str(x))

        sorted_json = sort_env_json(env_json)

        label_list = create_key_labels(sorted_json)

        updated_env_file = env_file_module.create_modified_env_file(sorted_json,
                                                                    label_list)

        try:
            env_file_module.set_env_file(s3_bucket, object_key,
                                         updated_env_file)
        except:
            logger.exception('AWS S3 put object failed')
            raise RuntimeError('AWS S3 put object failed')
        metrics.add_metric(name="UpdatedEnvFile", unit=MetricUnit.Count,
                           value=1)
        return destination_uris
