# -*- coding: utf-8 -*-
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView
)

from .models import (
    MPTTComment,
)


class MpttCommentCreateView(CreateView):
    model = MPTTComment


class MpttCommentDeleteView(DeleteView):
    model = MPTTComment


class MpttCommentDetailView(DetailView):
    model = MPTTComment


class MpttCommentUpdateView(UpdateView):
    model = MPTTComment


class MpttCommentListView(ListView):
    model = MPTTComment
