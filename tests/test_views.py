from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase, modify_settings, override_settings
from django.urls import reverse

from django_mptt_comments.models import MPTTComment
from django_mptt_comments.views import ReplySuccessView, ReplyView, post_mptt_comment
from crequest.middleware import CrequestMiddleware


class MPTTCommentsPostCommentTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='test', email='test@test.com', password='test')

    def test_authenticated_user_post_comment(self):
        self.client.login(username='test', password='test')
        response = self.client.post(reverse('mptt_comments_post_comment'), data={})
        self.assertEqual(response.status_code, 400)

    # TODO: override_settings doesn't work as control is module level.
    # see: https://docs.djangoproject.com/en/2.1/topics/testing/tools/#overriding-settings
    # @override_settings(MPTT_COMMENTS_ALLOW_ANONYMOUS=False)
    # def test_doesnt_allow_anonymous_user_post_comment(self):
    #     response = self.client.post(reverse('django_mptt_comments:mptt-comments-post-comment'), data={})
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(response.url, settings.LOGIN_URL + '?next=/post/')


class ReplyViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='test', email='test@test.com', password='test')
        site = Site.objects.create(name='test', domain='test.com')
        self.comment = MPTTComment.objects.create(**{
            'content_type': ContentType.objects.get_for_model(site),
            'object_pk': site.pk,
            'site': site,
            'user': self.user,
            'comment': 'test comment',
        })

    def test_reply(self):
        url = reverse('mptt_comments_reply', kwargs={'parent_id': self.comment.pk})
        request = self.factory.get(url)
        request.user = self.user
        CrequestMiddleware.set_request(request)
        response = ReplyView.as_view()(request, parent_id=self.comment.pk)

        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context_data)
        self.assertEqual(response.context_data['form'].initial['parent_id'], self.comment.pk)
