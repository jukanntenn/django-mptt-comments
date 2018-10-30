# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

app_name = 'blog'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^posts/(?P<pk>\d+)$', views.PostDetailView.as_view(), name='detail'),
]
