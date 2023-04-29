import re
import boto3
from botocore.exceptions import ClientError

from service.handlers.utils.observability import logger, tracer

# Get the .env file from AWS S3 Bucket


@tracer.capture_method(capture_response=False)
def get_env_file(bucket, key):
    logger.debug('Function: get_env_file invoked')
    client = boto3.client("s3")
    try:
        logger.info('Calling AWS S3 API on get_object')
        response = client.get_object(
            Bucket=bucket, Key=key
        )["Body"].read()
    except ClientError as error:
        if error.response['Error']['Code'] == 'NoSuchKey':
            logger.exception(f"Object key was not found in \
                             AWS S3 Bucket: {str(key)}", extra=bucket)
            raise ValueError('The object key provided in incorrect: {}'
                             .format(error))
        else:
            raise error
    return response

# Update the .env file in AWS S3 Bucket


@tracer.capture_method(capture_response=False)
def set_env_file(bucket, key, body):
    logger.debug('Function: set_env_file invoked')
    encoded_string = body.encode("utf-8")
    client = boto3.client('s3')
    try:
        logger.info('Calling AWS S3 API on put_object')
        response = client.put_object(Key=key, Body=encoded_string,
                                     Bucket=bucket)
    except ClientError as error:
        logger.exception(
            f"Unable to upload env file to S3 Bucket: {str(bucket)}")
        raise RuntimeError(
            'Unable to upload env file to S3 Bucket: {}'.format(error))
    return response

# Create new .env file to upload to AWS S3 Bucket


@tracer.capture_method(capture_response=False)
def create_modified_env_file(sorted_json, labels):
    logger.debug('Function: create_modified_env_file invoked')
    label_list = labels
    env_str = str()
    env_str += "# .ENV file managed by AWS ENV Management Library\n"
    env_str += "# Change Key/Value pairs in AWS System Manager\
      - Parameter Store\n"
    label_index = None
    for key in sorted_json:
        m = re.match(r"[a-zA-Z]*", key)
        L = m.group(0)
        if L != label_index:
            try:
                x = label_list.index(L)
            except IndexError as error:
                logger.warn(
                    f"Labeling error occured. Label does not exist\
                          in list: {str(L)}", extra=label_list)
            label_index = L
            c = "\n######## " + str(L) + " Variables Section #######\n\n"
            env_str += c
        env_str += key + "=" + sorted_json[key] + "\n"
    return env_str
