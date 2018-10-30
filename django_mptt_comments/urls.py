# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.urls import path, re_path

from . import views

from . import views

# app_name = 'django_mptt_comments'
urlpatterns = [
    url(r'^post/$', views.post_mptt_comment, name='mptt-comments-post-comment'),
    url(r'^reply/(?P<parent>[0-9]+)/$', views.ReplyView.as_view(), name='mptt_comments_reply'),
    url(r'^success/$',
        views.ReplySuccessView.as_view(),
        name='comment_success'),
    url('', include('django_comments.urls')),
]
