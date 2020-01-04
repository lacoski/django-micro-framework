import json


def data_to_json(data):
    return json.dumps(data)

def byte_to_string(data):
    return data.decode("utf8")

def redis_to_data(data):
    if isinstance(data, bytes):
        data = byte_to_string(data)
    return json.loads(data)
