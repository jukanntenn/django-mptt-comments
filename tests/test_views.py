from crequest.middleware import CrequestMiddleware
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse
from django_comments.views.comments import post_comment
from django_mptt_comments.decorators import conditional_login_required
from django_mptt_comments.models import MPTTComment
from django_mptt_comments.views.comments import (CommentEditView,
                                                 CommentSuccessRedirectView,
                                                 ReplyView)

from .models import RedirectTestModel


def get_post_mpttcomment_view():
    # `override_settings` doesn't work for module level constance,
    # thus we set view after overriding settings.
    post_mpttcomment_view = conditional_login_required(post_comment)
    return post_mpttcomment_view


class PostMPTTCommentTestCase(TestCase):
    def setUp(self):
        self.authenticated_user = User.objects.create_user(username='test', email='test@test.com', password='test')
        self.anonymous_user = AnonymousUser()
        self.factory = RequestFactory()
        self.request = self.factory.post(reverse('mptt_comments_post_mpttcomment'), data={})
        self.request.user = self.authenticated_user
        self.request._dont_enforce_csrf_checks = True  # disable csrf check

    def test_authenticated_user_can_comment_anyway(self):
        with override_settings(MPTT_COMMENTS={'ANONYMOUS_COMMENT_ALLOWED': False}):
            post_mpttcomment = get_post_mpttcomment_view()
            response = post_mpttcomment(self.request)
            self.assertEqual(response.status_code, 400)

        with override_settings(MPTT_COMMENTS={'ANONYMOUS_COMMENT_ALLOWED': True}):
            post_mpttcomment = get_post_mpttcomment_view()
            response = post_mpttcomment(self.request)
            self.assertEqual(response.status_code, 400)

    @override_settings(MPTT_COMMENTS={'ANONYMOUS_COMMENT_ALLOWED': False})
    def test_doesnt_allow_anonymous_comment(self):
        post_mpttcomment = get_post_mpttcomment_view()
        self.request.user = self.anonymous_user
        response = post_mpttcomment(self.request)
        self.assertEqual(response.status_code, 302)

    @override_settings(MPTT_COMMENTS={'ANONYMOUS_COMMENT_ALLOWED': True})
    def test_allow_anonymous_comment(self):
        post_mpttcomment = get_post_mpttcomment_view()
        self.request.user = self.anonymous_user
        response = post_mpttcomment(self.request)
        self.assertEqual(response.status_code, 400)


class ReplyViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.authenticated_user = User.objects.create_user(username='test', email='test@test.com', password='test')
        site = Site.objects.create(name='test', domain='test.com')
        self.comment = MPTTComment.objects.create(**{
            'content_type': ContentType.objects.get_for_model(site),
            'object_pk': site.pk,
            'site': site,
            'user': self.authenticated_user,
            'comment': 'test content',
        })

    def test_reply(self):
        url = reverse('mptt_comments_post_reply', kwargs={'parent_comment_pk': self.comment.pk})
        request = self.factory.get(url)
        request.user = self.authenticated_user
        CrequestMiddleware.set_request(request)
        response = ReplyView.as_view()(request, parent_comment_pk=self.comment.pk)

        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context_data)
        self.assertEqual(response.context_data['form'].initial['parent_comment_pk'], self.comment.pk)


class CommentSuccessRedirectViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.authenticated_user = User.objects.create_user(username='test', email='test@test.com', password='test')
        self.site = Site.objects.create(name='test', domain='test.com')
        self.comment = MPTTComment.objects.create(**{
            'content_type': ContentType.objects.get_for_model(self.site),
            'object_pk': self.site.pk,
            'site': self.site,
            'user': self.authenticated_user,
            'comment': 'test content',
        })

    def test_redirect_to_fallback(self):
        url = reverse('mptt_comments_comment_success') + '?c=%s' % self.comment.pk
        request = self.factory.get(url)
        response = CommentSuccessRedirectView.as_view()(request)
        self.assertEqual(response.url, reverse('comments-comment-done'))

    def test_redirect_to_comment(self):
        obj = RedirectTestModel.objects.create()
        comment = MPTTComment.objects.create(**{
            'content_type': ContentType.objects.get_for_model(obj),
            'object_pk': obj.pk,
            'site': self.site,
            'user': self.authenticated_user,
            'comment': 'test content',
        })

        url = reverse('mptt_comments_comment_success') + '?c=%s' % comment.pk
        request = self.factory.get(url)
        response = CommentSuccessRedirectView.as_view()(request)
        self.assertEqual(comment.get_absolute_url(), response.url)


class CommentEditViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.authenticated_user = User.objects.create_user(username='test', email='test@test.com', password='test')
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='test')
        self.super_user = User.objects.create_superuser(username='supertest', email='test@test.com', password='test')
        site = Site.objects.create(name='test', domain='test.com')
        self.comment = MPTTComment.objects.create(**{
            'content_type': ContentType.objects.get_for_model(site),
            'object_pk': site.pk,
            'site': site,
            'user': self.authenticated_user,
            'comment': 'test content',
        })

    def test_administrator_can_edit_anyway(self):
        with override_settings(MPTT_COMMENTS={'EDIT_COMMENT_ALLOWED': False}):
            url = reverse('mptt_comments_edit_mpttcomment', kwargs={'comment_pk': self.comment.pk})
            request = self.factory.get(url)
            request.user = self.super_user
            CrequestMiddleware.set_request(request)
            response = CommentEditView.as_view()(request, comment_pk=self.comment.pk)
            self.assertEqual(response.status_code, 200)

            request = self.factory.post(url, data={'comment': 'new content'})
            request.user = self.super_user
            CrequestMiddleware.set_request(request)
            response = CommentEditView.as_view()(request, comment_pk=self.comment.pk)
            self.assertEqual(response.status_code, 302)
            self.comment.refresh_from_db()
            self.assertEqual(self.comment.comment, 'new content')

        with override_settings(MPTT_COMMENTS={'EDIT_COMMENT_ALLOWED': True}):
            url = reverse('mptt_comments_edit_mpttcomment', kwargs={'comment_pk': self.comment.pk})
            request = self.factory.get(url)
            request.user = self.super_user
            CrequestMiddleware.set_request(request)
            response = CommentEditView.as_view()(request, comment_pk=self.comment.pk)
            self.assertEqual(response.status_code, 200)

            request = self.factory.post(url, data={'comment': 'new content'})
            request.user = self.super_user
            CrequestMiddleware.set_request(request)
            response = CommentEditView.as_view()(request, comment_pk=self.comment.pk)
            self.assertEqual(response.status_code, 302)
            self.comment.refresh_from_db()
            self.assertEqual(self.comment.comment, 'new content')

    @override_settings(MPTT_COMMENTS={'EDIT_COMMENT_ALLOWED': True})
    def test_allow_edit(self):
        url = reverse('mptt_comments_edit_mpttcomment', kwargs={'comment_pk': self.comment.pk})
        request = self.factory.get(url)
        request.user = self.authenticated_user
        CrequestMiddleware.set_request(request)
        response = CommentEditView.as_view()(request, comment_pk=self.comment.pk)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post(url, data={'comment': 'new content'})
        request.user = self.super_user
        CrequestMiddleware.set_request(request)
        response = CommentEditView.as_view()(request, comment_pk=self.comment.pk)
        self.assertEqual(response.status_code, 302)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.comment, 'new content')

    @override_settings(MPTT_COMMENTS={'EDIT_COMMENT_ALLOWED': False})
    def test_doesnt_not_allow_edit(self):
        url = reverse('mptt_comments_edit_mpttcomment', kwargs={'comment_pk': self.comment.pk})
        request = self.factory.get(url)
        request.user = self.authenticated_user
        CrequestMiddleware.set_request(request)
        response = CommentEditView.as_view()(request, comment_pk=self.comment.pk)
        self.assertEqual(response.status_code, 403)

        request = self.factory.post(url, data={'comment': 'new content'})
        request.user = self.authenticated_user
        CrequestMiddleware.set_request(request)
        response = CommentEditView.as_view()(request, comment_pk=self.comment.pk)
        self.assertEqual(response.status_code, 403)
        self.comment.refresh_from_db()
        self.assertEqual('test content', self.comment.comment)

    @override_settings(MPTT_COMMENTS={'EDIT_COMMENT_ALLOWED': True})
    def test_can_not_edit_comment_submitted_by_others(self):
        self.comment.user = self.other_user
        self.comment.save()
        self.comment.refresh_from_db()

        url = reverse('mptt_comments_edit_mpttcomment', kwargs={'comment_pk': self.comment.pk})
        request = self.factory.get(url)
        request.user = self.authenticated_user
        CrequestMiddleware.set_request(request)
        with self.assertRaises(PermissionDenied):
            CommentEditView.as_view()(request, comment_pk=self.comment.pk)

        request = self.factory.post(url, data={'comment': 'new content'})
        request.user = self.authenticated_user
        CrequestMiddleware.set_request(request)
        with self.assertRaises(PermissionDenied):
            CommentEditView.as_view()(request, comment_pk=self.comment.pk)
        self.comment.refresh_from_db()
        self.assertEqual('test content', self.comment.comment)
