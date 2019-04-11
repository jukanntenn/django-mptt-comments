from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django_comments import signals
from django_comments.views.utils import confirmation_view, next_redirect

from ..models import MPTTComment, MPTTCommentFlag


class FlagMPTTCommentView(LoginRequiredMixin, TemplateResponseMixin, SingleObjectMixin, View):
    template_name = 'comments/flag.html'
    context_object_name = 'comment'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        perform_flag(request, self.object)
        return next_redirect(request, fallback=self.object or 'comments-flag-done',
                             c=self.object.pk)


class DeleteMPTTCommentView(PermissionRequiredMixin, TemplateResponseMixin, SingleObjectMixin, View):
    permission_required = 'django_mptt_comments.can_moderate'
    template_name = 'django_mptt_comments/delete.html'
    context_object_name = 'comment'
    model = MPTTComment
    pk_url_kwarg = 'comment_pk'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        perform_delete(request, self.object)
        return next_redirect(request, fallback='mptt_comments_delete_done',
                             c=self.object.pk)


delete_done = confirmation_view(
    template="django_mptt_comments/deleted.html",
    doc="""Display a "comment was deleted" success page."""
)


class ApproveMPTTCommentView(PermissionRequiredMixin, TemplateResponseMixin, SingleObjectMixin, View):
    permission_required = 'django_mptt_comments.can_moderate'
    template_name = 'django_mptt_comments/approve.html'
    context_object_name = 'comment'
    model = MPTTComment
    pk_url_kwarg = 'comment_pk'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        perform_approve(request, self.object)
        return next_redirect(request, fallback='mptt_comments_approve_done',
                             c=self.object.pk)


approve_done = confirmation_view(
    template="django_mptt_comments/approved.html",
    doc="""Display a "comment was approved" success page."""
)


class HighlightMPTTCommentView(PermissionRequiredMixin, TemplateResponseMixin, SingleObjectMixin, View):
    permission_required = 'django_mptt_comments.can_moderate'
    template_name = 'django_mptt_comments/highlight.html'
    context_object_name = 'comment'
    model = MPTTComment
    pk_url_kwarg = 'comment_pk'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        perform_highlight(request, self.object)
        return next_redirect(request, fallback='mptt_comments_highlight_done',
                             c=self.object.pk)


highlight_done = confirmation_view(
    template="django_mptt_comments/highlighted.html",
    doc="""Display a "comment was highlighted" success page."""
)


class LikeMPTTCommentView(LoginRequiredMixin, TemplateResponseMixin, SingleObjectMixin, View):
    template_name = 'mptt_comments/like.html'
    context_object_name = 'comment'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        perform_like(request, self.object)
        return next_redirect(request, fallback=self.object or 'comments-like-done',
                             c=self.object.pk)


class DislikeMPTTCommentView(LoginRequiredMixin, TemplateResponseMixin, SingleObjectMixin, View):
    template_name = 'mptt_comments/dislike.html'
    context_object_name = 'comment'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        perform_dislike(request, self.object)
        return next_redirect(request, fallback=self.object or 'comments-dislike-done',
                             c=self.object.pk)


def perform_flag(request, comment):
    flag, created = MPTTCommentFlag.objects.get_or_create(
        comment=comment,
        user=request.user,
        flag=MPTTCommentFlag.SUGGEST_REMOVAL
    )
    signals.comment_was_flagged.send(
        sender=comment.__class__,
        comment=comment,
        flag=flag,
        created=created,
        request=request,
    )


def perform_delete(request, comment):
    flag, created = MPTTCommentFlag.objects.get_or_create(
        comment=comment,
        user=request.user,
        flag=MPTTCommentFlag.MODERATOR_DELETION
    )
    comment.is_removed = True
    comment.save()
    signals.comment_was_flagged.send(
        sender=comment.__class__,
        comment=comment,
        flag=flag,
        created=created,
        request=request,
    )


def perform_approve(request, comment):
    flag, created = MPTTCommentFlag.objects.get_or_create(
        comment=comment,
        user=request.user,
        flag=MPTTCommentFlag.MODERATOR_APPROVAL,
    )

    comment.is_removed = False
    comment.is_public = True
    comment.save()

    signals.comment_was_flagged.send(
        sender=comment.__class__,
        comment=comment,
        flag=flag,
        created=created,
        request=request,
    )


def perform_highlight(request, comment):
    flag, created = MPTTCommentFlag.objects.get_or_create(
        comment=comment,
        user=request.user,
        flag=MPTTCommentFlag.MODERATOR_HIGHLIGHT
    )
    signals.comment_was_flagged.send(
        sender=comment.__class__,
        comment=comment,
        flag=flag,
        created=created,
        request=request,
    )


def perform_like(request, comment):
    flag, created = MPTTCommentFlag.objects.get_or_create(
        comment=comment,
        user=request.user,
        flag=MPTTCommentFlag.ATTITUDE_LIKE
    )
    if not created:
        flag.delete()

    MPTTCommentFlag.objects.filter(
        comment=comment,
        user=request.user,
        flag=MPTTCommentFlag.ATTITUDE_DISLIKE
    ).delete()

    signals.comment_was_flagged.send(
        sender=comment.__class__,
        comment=comment,
        flag=flag,
        created=created,
        request=request,
    )


def perform_dislike(request, comment):
    flag, created = MPTTCommentFlag.objects.get_or_create(
        comment=comment,
        user=request.user,
        flag=MPTTCommentFlag.ATTITUDE_DISLIKE
    )
    if not created:
        flag.delete()

    MPTTCommentFlag.objects.filter(
        comment=comment,
        user=request.user,
        flag=MPTTCommentFlag.ATTITUDE_LIKE
    ).delete()

    signals.comment_was_flagged.send(
        sender=comment.__class__,
        comment=comment,
        flag=flag,
        created=created,
        request=request,
    )
