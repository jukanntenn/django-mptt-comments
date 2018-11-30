from django.conf import settings
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension

_DEFAULT_ALLOWED_TAGS = [
    'address', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'dd', 'div',
    'dl', 'dt', 'figcaption', 'figure', 'hr', 'li', 'ol', 'p', 'pre', 'ul',
    'a', 'abbr', 'b', 'br', 'cite', 'code', 'em', 'i', 'kbd', 'mark', 'q', 's',
    'small', 'span', 'strong', 'sub', 'sup', 'time', 'tt', 'u', 'img', 'del',
    'ins', 'caption', 'col', 'colgroup', 'table', 'tbody', 'td', 'tfoot', 'th',
    'thead', 'tr', 'dfn', 'acronym',
]

_DEFAULT_ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'abbr': ['title'],
    'acronym': ['title'],
    'span': ['class'],
    '*': ['id'],
    'img': ['src'],
}

_DEFAULT_MARKDOWN_EXTENSIONS = [
    'markdown.extensions.extra',
    'markdown.extensions.codehilite',
    TocExtension(slugify=slugify),
]

ALLOW_ANONYMOUS = getattr(
    settings,
    'MPTT_COMMENTS_ALLOW_ANONYMOUS',
    True
)

ALLOWED_TAGS = getattr(
    settings,
    'MPTT_COMMENTS_ALLOWED_TAGS',
    _DEFAULT_ALLOWED_TAGS
)

ALLOWED_ATTRIBUTES = getattr(
    settings,
    'MPTT_COMMENTS_ALLOWED_ATTRIBUTES',
    _DEFAULT_ALLOWED_ATTRIBUTES
)

MARKDOWN_EXTENSIONS = getattr(
    settings,
    'MPTT_COMMENTS_MARKDOWN_EXTENSIONS',
    _DEFAULT_MARKDOWN_EXTENSIONS
)
