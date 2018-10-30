__version__ = '0.1.0'

from django.urls import reverse


def get_model():
    from .models import MPTTComment
    return MPTTComment


def get_form():
    from .forms import MPTTCommentForm
    return MPTTCommentForm


def get_form_target():
    return reverse('mptt-comments-post-comment')
