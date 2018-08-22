# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.views.generic import TemplateView

from . import views

from .views import post_mptt_comment

app_name = 'django_mptt_comments'
urlpatterns = [
    url(r'^post/$', post_mptt_comment, name='mptt-comments-post-comment'),
    url('', include('django_comments.urls')),
]
