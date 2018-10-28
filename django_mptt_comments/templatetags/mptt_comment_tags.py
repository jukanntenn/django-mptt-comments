from django import template
from django_comments.templatetags.comments import RenderCommentFormNode

import django_mptt_comments

register = template.Library()


class RenderMPTTCommentFormNode(RenderCommentFormNode):
    def get_form(self, context):
        obj = self.get_object(context)
        user = context['request'].user
        if obj:
            return django_mptt_comments.get_form()(obj, user=user)
        else:
            return None


@register.tag
def render_mptt_comment_form(parser, token):
    return RenderMPTTCommentFormNode.handle_token(parser, token)
