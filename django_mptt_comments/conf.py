from collections import ChainMap

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

DEFAULT_COMMENT_HTML_TAG_WHITELIST = [
    'address', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'dd', 'div',
    'dl', 'dt', 'figcaption', 'figure', 'hr', 'li', 'ol', 'p', 'pre', 'ul',
    'a', 'abbr', 'b', 'br', 'cite', 'code', 'em', 'i', 'kbd', 'mark', 'q', 's',
    'small', 'span', 'strong', 'sub', 'sup', 'time', 'tt', 'u', 'img', 'del',
    'ins', 'caption', 'col', 'colgroup', 'table', 'tbody', 'td', 'tfoot', 'th',
    'thead', 'tr', 'dfn', 'acronym',
]

DEFAULT_COMMENT_HTML_ATTRIBUTE_WHITELIST = {
    'a': ['href', 'title'],
    'abbr': ['title'],
    'acronym': ['title'],
    'span': ['class'],
    '*': ['id'],
    'img': ['src'],
}


class Settings(object):
    defaults = {
        'ANONYMOUS_COMMENT_ALLOWED': False,
        'EDIT_COMMENT_ALLOWED': False,

        'COMMENT_HTML_TAG_WHITELIST': DEFAULT_COMMENT_HTML_TAG_WHITELIST,
        'COMMENT_HTML_ATTRIBUTE_WHITELIST': DEFAULT_COMMENT_HTML_ATTRIBUTE_WHITELIST,
    }

    def __getattr__(self, attribute):
        user_settings = getattr(django_settings, 'MPTT_COMMENTS', {})
        if attribute in self.defaults:
            return ChainMap(user_settings, self.defaults).get(attribute)
        raise ImproperlyConfigured("django-mptt-comments doesn't have such setting: %s." % attribute)


settings = Settings()
