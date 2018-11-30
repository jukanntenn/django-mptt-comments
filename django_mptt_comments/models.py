# -*- coding: utf-8 -*-
import bleach
import markdown
from django.db import models
from django.db.models import TextField
from django.utils.translation import ugettext_lazy as _
from django_comments.models import CommentAbstractModel
from mptt.models import MPTTModel, TreeForeignKey

from .conf import MARKDOWN_EXTENSIONS
from .utils import bleach_value


class MarkedTextField(TextField):
    """
    A TextField that populate value from ``source`` field,
    then convert the value to marked value (using markdown library).
    """
    description = _("Marked text")

    def __init__(self, source, *args, **kwargs):
        self.source = source
        kwargs.setdefault('editable', False)
        super(TextField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        instance = model_instance
        value = None

        for attr in self.source.split('.'):
            value = getattr(instance, attr)
            instance = value

        if value is None or value == '':
            return value

        md = markdown.Markdown(extensions=MARKDOWN_EXTENSIONS)
        # Markdown 文本测试存在一个问题，如果原始 html 文本下跟一段 fenced 代码段，
        # 代码段无法被正常渲染
        # TODO：解决此问题
        value = md.convert(value)
        value = bleach_value(value)
        # linkify 会过滤 pre 标签中的 span 标签，目前没有找到解决方案
        # TODO: linkify 解决方案
        # value = bleach.linkify(value, skip_tags=['pre'])
        setattr(model_instance, self.attname, value)

        return value

    def deconstruct(self):
        name, path, args, kwargs = super(TextField, self).deconstruct()
        args.append(self.source)

        return name, path, args, kwargs


class MPTTComment(MPTTModel, CommentAbstractModel):
    parent = TreeForeignKey('self', verbose_name=_('parent comment'),
                            blank=True, null=True,
                            related_name='children', on_delete=models.SET_NULL)
    comment_html = MarkedTextField(source='comment',
                                   verbose_name=_('comment (html)'),
                                   blank=True)

    class Meta(CommentAbstractModel.Meta):
        ordering = ['-submit_date']
        verbose_name = _('mptt comment')
        verbose_name_plural = _('mptt comments')

    class MPTTMeta:
        order_insertion_by = ['submit_date']
