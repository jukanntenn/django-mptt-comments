from django.db import models

from django_mptt_comments.models import MarkedTextField


class MarkedTextFieldTestModel(models.Model):
    body = models.TextField(blank=True)
    body_html = MarkedTextField(source='body')


class MarkedTextFieldBadSourceTestModel(models.Model):
    body = models.TextField(blank=True)
    body_html = MarkedTextField(source='bad')


class RedirectTestModel(models.Model):
    body = models.TextField(blank=True)

    def get_absolute_url(self):
        return '/test/'
