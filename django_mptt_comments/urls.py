# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.views.generic import TemplateView

from . import views

app_name = 'django_mptt_comments'
urlpatterns = [
    url(
        regex="^MpttComment/~create/$",
        view=views.MpttCommentCreateView.as_view(),
        name='MpttComment_create',
    ),
    url(
        regex="^MpttComment/(?P<pk>\d+)/~delete/$",
        view=views.MpttCommentDeleteView.as_view(),
        name='MpttComment_delete',
    ),
    url(
        regex="^MpttComment/(?P<pk>\d+)/$",
        view=views.MpttCommentDetailView.as_view(),
        name='MpttComment_detail',
    ),
    url(
        regex="^MpttComment/(?P<pk>\d+)/~update/$",
        view=views.MpttCommentUpdateView.as_view(),
        name='MpttComment_update',
    ),
    url(
        regex="^MpttComment/$",
        view=views.MpttCommentListView.as_view(),
        name='MpttComment_list',
    ),
]
