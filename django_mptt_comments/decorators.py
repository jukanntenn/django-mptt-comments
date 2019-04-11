from django.contrib.auth.decorators import login_required
from .conf import settings


def conditional_login_required(func):
    if not settings.ANONYMOUS_COMMENT_ALLOWED:
        return login_required(func)
    return func
