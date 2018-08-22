from django.test import RequestFactory, TestCase

from django_mptt_comments.views import post_mptt_comment
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser, User
from django.test import override_settings, modify_settings
from django.conf import settings


class MPTTCommentsPostCommentTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='test', email='test@test.com', password='test')

    def test_authenticated_user_post_comment(self):
        self.client.login(username='test', password='test')
        response = self.client.post(reverse('django_mptt_comments:mptt-comments-post-comment'), data={})
        self.assertEqual(response.status_code, 400)

    # TODO: override_settings doesn't work as control is module level.
    # see: https://docs.djangoproject.com/en/2.1/topics/testing/tools/#overriding-settings
    # @override_settings(MPTT_COMMENTS_ALLOW_ANONYMOUS=False)
    # def test_doesnt_allow_anonymous_user_post_comment(self):
    #     response = self.client.post(reverse('django_mptt_comments:mptt-comments-post-comment'), data={})
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(response.url, settings.LOGIN_URL + '?next=/post/')
