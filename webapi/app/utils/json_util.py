import json
from datetime import datetime


def deserialize_object(json_str: str, object_class=None):
    if object_class is None:
        return json.loads(json_str)
    return object_class(**json.loads(json_str))


def serialize_object(obj):
    def default_serializer(o):
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        raise TypeError(f"Object of type {type(o)} is not JSON serializable")
    
    return json.dumps(obj, default=default_serializer, ensure_ascii=False, indent=2)


def serialize_to_dict(obj):
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return obj
