import django_comments
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DetailView, RedirectView
from django.views.generic.edit import FormMixin
from django_comments.views.comments import post_comment

from .forms import MPTTCommentForm
from .models import MPTTComment

from .conf import MPTT_COMMENTS_ALLOW_ANONYMOUS

if MPTT_COMMENTS_ALLOW_ANONYMOUS:
    post_mptt_comment = post_comment
else:
    post_mptt_comment = login_required(post_comment)


class ReplyView(FormMixin, DetailView):
    model = MPTTComment
    form_class = MPTTCommentForm
    pk_url_kwarg = 'parent_id'
    template_name = 'django_mptt_comments/reply.html'

    def get_form_kwargs(self):
        kwargs = super(ReplyView, self).get_form_kwargs()
        kwargs.update({
            'target_object': self.object.content_object,
            'parent_id': self.object.pk,
        })
        return kwargs


class CommentSuccessRedirectView(RedirectView):
    pattern_name = 'comments-comment-done'  # 如果跳转回新评论页面失败，就会跳转到这个页面

    def dispatch(self, request, *args, **kwargs):
        if 'c' in request.GET:
            try:
                self.comment = django_comments.get_model().objects.get(
                    pk=request.GET['c'])
            except (ObjectDoesNotExist, ValueError):
                pass
        return super(CommentSuccessRedirectView, self).dispatch(request, *args,
                                                                **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        try:
            comment = self.comment
            comment.content_object.get_absolute_url()  # 没有 get_absolute_url 方法后续跳转不会成功

            if self.comment.is_public and not self.comment.is_removed:
                self.url = comment.get_absolute_url()
        except AttributeError:
            pass
        return super(CommentSuccessRedirectView, self).get_redirect_url(*args,
                                                                        **kwargs)
