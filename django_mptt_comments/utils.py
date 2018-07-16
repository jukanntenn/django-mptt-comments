import bleach

BLEACH_ALLOWED_TAGS = ['p', 'pre', 'blockquote', 'ol', 'ul', 'li', 'dl', 'dt', 'dd', 'figure', 'figcaption', 'hr', 'a',
                       'em', 'strong', 'cite', 'q', 'dfn', 'abbr', 'time', 'code', 'br', 'i', 'b', 'u', 's', 'sub',
                       'sup',
                       'ins', 'del', 'img', 'table', 'tr', 'td', 'th', 'caption', 'tbody', 'thead', 'tfoot', 'colgroup',
                       'col',
                       'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'acronym', 'span']

BLEACH_ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'abbr': ['title'],
    'acronym': ['title'],
    'span': ['class'],
    '*': ['id'],
    'img': ['src'],
}


def bleach_value(value, tags=BLEACH_ALLOWED_TAGS, attributes=BLEACH_ALLOWED_ATTRIBUTES):
    return bleach.clean(value, tags=tags, attributes=attributes)
