import django_comments
from django.conf import settings as django_settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http.response import HttpResponseForbidden
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from django.views.generic.edit import FormMixin
from django_comments import signals
from django_comments.views.comments import post_comment
from django_comments.views.utils import confirmation_view

from ..conf import settings
from ..forms import CommentEditForm, MPTTCommentForm
from ..mixins import ConditionalLoginRequiredMixin
from ..models import MPTTCommentFlag, MPTTComment
from ..decorators import conditional_login_required

post_mpttcomment = conditional_login_required(post_comment)
edit_done = confirmation_view(
    template="mptt_comments/edited.html",
    doc="""Display a "comment was edited" success page."""
)


class ReplyView(ConditionalLoginRequiredMixin, FormMixin, DetailView):
    model = MPTTComment
    form_class = MPTTCommentForm
    pk_url_kwarg = 'parent_comment_pk'
    template_name = 'mptt_comments/reply.html'

    def get_form_kwargs(self):
        kwargs = super(ReplyView, self).get_form_kwargs()
        kwargs.update({
            'target_object': self.object.content_object,
            'parent_comment_pk': self.object.pk,
        })
        return kwargs


class CommentSuccessRedirectView(RedirectView):
    pattern_name = 'comments-comment-done'

    def dispatch(self, request, *args, **kwargs):
        if 'c' in request.GET:
            try:
                comment_pk = int(request.GET['c'])
                comment = django_comments.get_model().objects.get(pk=comment_pk)
                setattr(self, 'comment', comment)
            except ValueError:
                pass
            except ObjectDoesNotExist:
                pass
        return super(CommentSuccessRedirectView, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        comment = getattr(self, 'comment', None)
        if comment is not None:
            if comment.is_public and not comment.is_removed:
                if hasattr(comment.content_object, 'get_absolute_url'):
                    self.url = comment.get_absolute_url()
        return super(CommentSuccessRedirectView, self).get_redirect_url(*args, **kwargs)


class CommentEditView(LoginRequiredMixin, UpdateView):
    model = MPTTComment
    form_class = CommentEditForm
    pk_url_kwarg = 'comment_pk'
    template_name = 'mptt_comments/edit.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            if not settings.EDIT_COMMENT_ALLOWED:
                return HttpResponseForbidden(_('Does not allow edit.'))
        return super(CommentEditView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if hasattr(self.object.content_object, 'get_absolute_url'):
            return super(CommentEditView, self).get_success_url()
        return reverse('mptt_comments_edit_done')

    def get_object(self, queryset=None):
        obj = super(CommentEditView, self).get_object(queryset=queryset)
        user = self.request.user
        if not user.is_superuser and user != obj.user:
            raise PermissionDenied(_('Does not allow edit.'))
        return obj
