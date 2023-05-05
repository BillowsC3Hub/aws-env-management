import json
import hashlib
from aws_lambda_powertools.utilities.parser import BaseModel, validator

# List of objects located in the event.Messages variable. Supplied by AWS SQS
MESSAGE_OBJECTS = ['Body', 'Md5OfBody', 'MessageId', 'ReceiptHandle']

# Input validation model


class Input(BaseModel):
    Messages: list

    @validator('Messages')
    def check_list_items_exist(cls, v):
        x = {}
        i = 0
        for m in v:
            x = v[i]
            z = list(x.keys())
            print(z)
            for y in MESSAGE_OBJECTS:
                if (z.count(y) != 1):
                    raise ValueError(
                        f'Message Object key missing: {str(y)}')
            x = {}
            i += 1
        return v

    @validator('Messages')
    def validate_body_is_JSON_str(cls, v):
        i = 0
        for m in v:
            try:
                json.loads(v[i]['Body'])
            except ValueError as err:
                raise ValueError('Message Body invalid JSON')
            i += 1
        return v

    @validator('Messages')
    def validate_hd5_hash(cls, v):
        i = 0
        for m in v:
            b = v[i]['Body']
            d = v[i]['Md5OfBody']
            e = b.encode('utf-8')
            h = hashlib.md5(e).hexdigest()
            if h != d:
                raise ValueError(
                    'Messages Body did not pass hash validation')
        return v
