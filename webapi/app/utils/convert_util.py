from datetime import datetime


def min_date():
    return datetime(1900, 1, 1)


def obj_to_int(value, default=0):
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def obj_to_float(value, default=0.0):
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def obj_to_decimal(value, default=0.0):
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def obj_to_str(value, default=""):
    if value is None:
        return default
    return str(value).strip()


def obj_to_date(value, default=None):
    if default is None:
        default = min_date()
    if value is None:
        return default
    try:
        if isinstance(value, datetime):
            return value
        return datetime.strptime(str(value), "%Y-%m-%d")
    except (ValueError, TypeError):
        return default


def obj_to_bool(value, default=False):
    if value is None:
        return default
    try:
        return bool(value)
    except (ValueError, TypeError):
        return default
