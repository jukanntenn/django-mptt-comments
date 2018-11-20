from django.views.generic import ListView, DetailView

from .models import Post


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
