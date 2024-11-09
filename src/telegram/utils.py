import typing
from datetime import datetime

from telethon.tl import types as telethon_types_module, functions, TLObject, TLRequest


def require_subclass(subclass_name: type):
    return lambda element: issubclass(element, subclass_name)


def get_elements(module, check_func: typing.Callable) -> dict:
    elements = dict()
    for element_name in dir(module):
        element = getattr(module, element_name)
        if type(element).__name__ == "module" and element.__package__.startswith("telethon"):
            elements.update(get_elements(element, check_func))
        elif type(element) == type and check_func(element):
            elements[element_name] = element
    return elements


tl_objects = get_elements(telethon_types_module, require_subclass(TLObject))
tl_requests = get_elements(functions, require_subclass(TLRequest))
tl_all = {**tl_requests, **tl_objects}


def convert_from_pre_json(value):
    if isinstance(value, dict):
        return {key: convert_from_pre_json(value) for key, value in value.items()}
    elif isinstance(value, list):
        return [convert_from_pre_json(item) for item in value]
    elif type(value).__name__ == "str" and value.startswith("_*t:"):
        return datetime.fromisoformat(value[4:])
    elif type(value).__name__ == "str" and value.startswith("_*b:"):
        return bytes.fromhex(value[4:])
    return value


def convert_to_pre_json(value):
    if isinstance(value, TLObject):
        return convert_to_pre_json(value.to_dict())
    elif isinstance(value, dict):
        return {key: convert_to_pre_json(value) for key, value in value.items()}
    elif isinstance(value, list):
        return [convert_to_pre_json(item) for item in value]
    elif type(value).__name__ == "datetime":
        return f"_*t:{value}"
    elif type(value).__name__ == "bytes":
        return f"_*b:{value.hex()}"
    return value


def convert_objects_from_dict(value):
    if isinstance(value, dict) and value.get("_"):
        return tl_all.get(value.pop("_"))(**convert_objects_from_dict(value))
    if isinstance(value, dict):
        return {key: convert_objects_from_dict(value) for key, value in value.items()}
    elif isinstance(value, list):
        return [convert_objects_from_dict(item) for item in value]
    return value