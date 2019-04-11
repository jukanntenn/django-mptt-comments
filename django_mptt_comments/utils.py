import bleach

from .conf import settings


def bleach_value(value, tags=settings.COMMENT_HTML_TAG_WHITELIST, attributes=settings.COMMENT_HTML_ATTRIBUTE_WHITELIST):
    return bleach.clean(value, tags=tags, attributes=attributes)
