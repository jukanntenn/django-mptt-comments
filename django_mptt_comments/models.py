# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_comments.models import CommentAbstractModel
from mptt.models import MPTTModel, TreeForeignKey


class MpttComment(MPTTModel, CommentAbstractModel):
    parent = TreeForeignKey('self', verbose_name=_('parent comment'), blank=True, null=True,
                            related_name='children', on_delete=models.SET_NULL)
    comment_html = models.TextField(_('comment (html)'), blank=True)

    class Meta(CommentAbstractModel.Meta):
        ordering = ['-submit_date']
        verbose_name = _('mptt comment')
        verbose_name_plural = _('mptt comments')

    class MPTTMeta:
        order_insertion_by = ['submit_date']
