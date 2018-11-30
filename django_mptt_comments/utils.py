import bleach

from .conf import ALLOWED_ATTRIBUTES, ALLOWED_TAGS


def bleach_value(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES):
    return bleach.clean(value, tags=tags, attributes=attributes)
