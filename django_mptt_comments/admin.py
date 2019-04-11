from django.contrib import admin
from django.utils.translation import ungettext
from django_comments.admin import CommentsAdmin

from .models import MPTTComment
from .views.moderation import (perform_approve, perform_delete, perform_flag,
                             perform_highlight)


class MPTTCommentAdmin(CommentsAdmin):
    def flag_comments(self, request, queryset):
        self._bulk_flag(request, queryset, perform_flag,
                        lambda n: ungettext('flagged', 'flagged', n))

    def approve_comments(self, request, queryset):
        self._bulk_flag(request, queryset, perform_approve,
                        lambda n: ungettext('approved', 'approved', n))

    def remove_comments(self, request, queryset):
        self._bulk_flag(request, queryset, perform_delete,
                        lambda n: ungettext('removed', 'removed', n))

    def highlight_comments(self, request, queryset):
        self._bulk_flag(request, queryset, perform_highlight,
                        lambda n: ungettext('removed', 'removed', n))


admin.site.register(MPTTComment, MPTTCommentAdmin)
