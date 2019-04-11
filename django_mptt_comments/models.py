import bleach

import django_comments
import markdown
from django.conf import settings as django_settings
from django.db import models
from django.db.models import TextField
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django_comments.models import CommentAbstractModel
from mptt.models import MPTTModel, TreeForeignKey

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

        md = markdown.Markdown(extensions=[])
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


comment_model = django_comments.get_model()


@python_2_unicode_compatible
class MPTTCommentFlag(models.Model):
    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE,
    )
    comment = models.ForeignKey(
        # Translators: 'comment' is a noun here.
        comment_model, verbose_name=_('comment'), on_delete=models.CASCADE,
    )
    # Translators: 'flag' is a noun here.
    flag = models.CharField(_('flag'), max_length=30, db_index=True)
    flag_date = models.DateTimeField(_('date'), default=None)

    # Constants for flag types
    SUGGEST_REMOVAL = "removal suggestion"
    MODERATOR_DELETION = "moderator deletion"
    MODERATOR_APPROVAL = "moderator approval"
    MODERATOR_HIGHLIGHT = "moderator highlight"
    LIKE = "like"
    DISLIKE = "dislike"

    class Meta:
        unique_together = [('user', 'comment', 'flag')]
        verbose_name = _('mpttcomment flag')
        verbose_name_plural = _('mpttcomment flags')

    def __str__(self):
        return "%s flag of comment ID %s by %s" % (
            self.flag, self.comment_id, self.user.get_username()
        )

    def save(self, *args, **kwargs):
        if self.flag_date is None:
            self.flag_date = timezone.now()
        super(MPTTCommentFlag, self).save(*args, **kwargs)
