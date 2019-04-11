from django.conf.urls import include, url

from .views import comments as comment_views
from .views import moderation as moderation_views

urlpatterns = [
    url(r'^post/$', comment_views.post_mpttcomment, name='mptt_comments_post_mpttcomment',
        kwargs={'next': 'mptt_comments_comment_success'}),
    url(r'^reply/(?P<parent_comment_pk>[0-9]+)/$', comment_views.ReplyView.as_view(), name='mptt_comments_post_reply'),
    url(r'^success/$', comment_views.CommentSuccessRedirectView.as_view(), name='mptt_comments_comment_success'),
    url(r'^edit/(?P<comment_pk>[0-9]+)/$', comment_views.CommentEditView.as_view(),
        name='mptt_comments_edit_mpttcomment'),
    url(r'^edited/$', comment_views.edit_done, name='mptt_comments_edit_done'),

    url(r'^highlight/(?P<comment_pk>[0-9]+)/$', moderation_views.HighlightMPTTCommentView.as_view(),
        name='mptt_comments_highlight'),
    url(r'^highlighted/$', moderation_views.highlight_done,
        name='mptt_comments_highlight_done'),

    url(r'^approve/(?P<comment_pk>[0-9]+)/$', moderation_views.ApproveMPTTCommentView.as_view(),
        name='mptt_comments_approve'),
    url(r'^approved/$', moderation_views.approve_done,
        name='mptt_comments_approve_done'),

    url(r'^delete/(?P<comment_pk>[0-9]+)/$', moderation_views.DeleteMPTTCommentView.as_view(),
        name='mptt_comments_delete'),
    url(r'^deleted/$', moderation_views.delete_done,
        name='mptt_comments_delete_done'),

    url(r'^flag/(?P<comment_pk>[0-9]+)/$', moderation_views.FlagMPTTCommentView.as_view(),
        name='mptt_comments_flag'),
    url(r'^flagged/$', moderation_views.flag_done,
        name='mptt_comments_flag_done'),

    url(r'^like/(?P<comment_pk>[0-9]+)/$', moderation_views.LikeMPTTCommentView.as_view(),
        name='mptt_comments_like'),
    url(r'^liked/$', moderation_views.like_done,
        name='mptt_comments_like_done'),

    url(r'^dislike/(?P<comment_pk>[0-9]+)/$', moderation_views.DislikeMPTTCommentView.as_view(),
        name='mptt_comments_dislike'),
    url(r'^disliked/$', moderation_views.dislike_done,
        name='mptt_comments_dislike_done'),

    url(r'^', include('django_comments.urls')),
]
