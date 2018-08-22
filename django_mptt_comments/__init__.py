__version__ = '0.1.0'


def get_model():
    from .models import MPTTComment
    return MPTTComment


def get_form():
    from .forms import MPTTCommentForm
    return MPTTCommentForm
