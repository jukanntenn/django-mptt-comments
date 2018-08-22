# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('django_mptt_comments.urls')),
    url(r'^', include('captcha.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
]
