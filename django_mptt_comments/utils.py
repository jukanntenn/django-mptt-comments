import bleach

from .conf import ALLOWED_ATTRIBUTES, ALLOWED_TAGS


def bleach_value(value, tags=ALLOWED_ATTRIBUTES, attributes=ALLOWED_TAGS):
    return bleach.clean(value, tags=tags, attributes=attributes)
