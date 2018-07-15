# -*- coding: utf-8 -*-
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView
)

from .models import (
	MpttComment,
)


class MpttCommentCreateView(CreateView):

    model = MpttComment


class MpttCommentDeleteView(DeleteView):

    model = MpttComment


class MpttCommentDetailView(DetailView):

    model = MpttComment


class MpttCommentUpdateView(UpdateView):

    model = MpttComment


class MpttCommentListView(ListView):

    model = MpttComment

