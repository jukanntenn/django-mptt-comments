from django_comments.views.comments import post_comment as post_comment
from django.contrib.auth.decorators import login_required
from django.conf import settings

if settings.MPTT_COMMENTS_ALLOW_ANONYMOUS:
    post_mptt_comment = post_comment
else:
    post_mptt_comment = login_required(post_comment)
