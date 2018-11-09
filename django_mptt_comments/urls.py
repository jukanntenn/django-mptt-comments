# -*- coding: utf-8 -*-
from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^post/$', views.post_mptt_comment, name='mptt_comments_post_comment'),
    url(r'^reply/(?P<parent_id>[0-9]+)/$', views.ReplyView.as_view(), name='mptt_comments_reply'),
    url(r'^success/$', views.ReplySuccessView.as_view(), name='mptt_comments_reply_success'),

    url(r'^', include('django_comments.urls')),
]
