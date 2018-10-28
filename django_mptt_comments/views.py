import django_comments
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DetailView, RedirectView
from django.views.generic.edit import FormMixin
from django_comments.views.comments import post_comment

from .forms import MPTTCommentForm
from .models import MPTTComment

if settings.MPTT_COMMENTS_ALLOW_ANONYMOUS:
    post_mptt_comment = post_comment
else:
    post_mptt_comment = login_required(post_comment)


class ReplyView(FormMixin, DetailView):
    model = MPTTComment
    form_class = MPTTCommentForm
    pk_url_kwarg = 'parent'
    template_name = 'django_mptt_comments/reply.html'

    def get_form_kwargs(self):
        kwargs = super(ReplyView, self).get_form_kwargs()
        kwargs.update({
            'target_object': self.object.content_object,
            'parent': self.object.pk,
            'user': self.request.user
        })
        return kwargs


class ReplySuccessView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        self.url = self.comment.get_absolute_url()
        return super(ReplySuccessView, self).get_redirect_url(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.comment = None
        if 'c' in request.GET:
            try:
                self.comment = django_comments.get_model().objects.get(
                    pk=request.GET['c'])
            except (ObjectDoesNotExist, ValueError):
                pass
        if self.comment and self.comment.is_public:
            return super(ReplySuccessView, self).get(request, *args, **kwargs)
