from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from django_comments import signals
from django_mptt_comments.models import MPTTComment, MPTTCommentFlag

CT = ContentType.objects.get_for_model


def make_moderator(username):
    u = User.objects.get(username=username)
    ct = ContentType.objects.get_for_model(MPTTComment)
    p = Permission.objects.get(content_type=ct, codename="can_moderate")
    u.user_permissions.add(p)


class HighlightViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="moderator",
            password="test123456",
            is_staff=True,
            is_superuser=False,
        )

        self.comment = MPTTComment.objects.create(
            content_type=CT(Site),
            object_pk="1",
            user_name="Somebody",
            user_email="Somebody@example.com",
            comment="Some text",
            site=Site.objects.get_current(),
        )

    def test_highlight_permissions(self):
        pk = self.comment.pk
        self.client.login(username="moderator", password="test123456")
        response = self.client.get("/highlight/%d/" % pk)
        self.assertEqual(response.status_code, 403)

        make_moderator("moderator")

        response = self.client.get("/highlight/%d/" % pk)
        self.assertEqual(response.status_code, 200)

    def test_highlight_post(self):
        pk = self.comment.pk
        make_moderator("moderator")
        self.client.login(username="moderator", password="test123456")
        response = self.client.post("/highlight/%d/" % pk)
        self.assertRedirects(response, "/highlighted/?c=%d" % pk)
        c = MPTTComment.objects.get(pk=pk)
        self.assertEqual(
            c.mpttcommentflag_set.filter(flag=MPTTCommentFlag.MODERATOR_HIGHLIGHT, user__username="moderator").count(),
            1
        )

    def test_highlight_post_next(self):
        pk = self.comment.pk
        make_moderator("moderator")
        self.client.login(username="moderator", password="test123456")
        response = self.client.post("/highlight/%d/" % pk, data={'next': '/go/here/'})
        self.assertRedirects(response, "/go/here/?c=%d" % pk, fetch_redirect_response=False)
        c = MPTTComment.objects.get(pk=pk)
        self.assertEqual(
            c.mpttcommentflag_set.filter(flag=MPTTCommentFlag.MODERATOR_HIGHLIGHT, user__username="moderator").count(),
            1
        )

    def test_highlight_signals(self):
        def receive(sender, **kwargs):
            received_signals.append(kwargs.get('signal'))

        # Connect signals and keep track of handled ones
        received_signals = []
        signals.comment_was_flagged.connect(receive)

        # Post a comment and check the signals
        self.test_highlight_post()
        self.assertEqual(received_signals, [signals.comment_was_flagged])

        signals.comment_was_flagged.disconnect(receive)


class ApproveViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="moderator",
            password="test123456",
            is_staff=True,
            is_superuser=False,
        )

        self.comment = MPTTComment.objects.create(
            content_type=CT(Site),
            object_pk="1",
            user_name="Somebody",
            user_email="Somebody@example.com",
            comment="Some text",
            site=Site.objects.get_current(),
        )

    def test_approve_permissions(self):
        pk = self.comment.pk
        self.client.login(username="moderator", password="test123456")
        response = self.client.get("/approve/%d/" % pk)
        self.assertEqual(response.status_code, 403)

        make_moderator("moderator")

        response = self.client.get("/approve/%d/" % pk)
        self.assertEqual(response.status_code, 200)

    def test_approve_post(self):
        pk = self.comment.pk
        make_moderator("moderator")
        self.client.login(username="moderator", password="test123456")
        response = self.client.post("/approve/%d/" % pk)
        self.assertRedirects(response, "/approved/?c=%d" % pk)
        c = MPTTComment.objects.get(pk=pk)
        self.assertEqual(
            c.mpttcommentflag_set.filter(flag=MPTTCommentFlag.MODERATOR_APPROVAL, user__username="moderator").count(),
            1
        )

    def test_approve_post_next(self):
        pk = self.comment.pk
        make_moderator("moderator")
        self.client.login(username="moderator", password="test123456")
        response = self.client.post("/approve/%d/" % pk, data={'next': '/go/here/'})
        self.assertRedirects(response, "/go/here/?c=%d" % pk, fetch_redirect_response=False)
        c = MPTTComment.objects.get(pk=pk)
        self.assertEqual(
            c.mpttcommentflag_set.filter(flag=MPTTCommentFlag.MODERATOR_APPROVAL, user__username="moderator").count(),
            1
        )

    def test_approve_signals(self):
        def receive(sender, **kwargs):
            received_signals.append(kwargs.get('signal'))

        # Connect signals and keep track of handled ones
        received_signals = []
        signals.comment_was_flagged.connect(receive)

        # Post a comment and check the signals
        self.test_approve_post()
        self.assertEqual(received_signals, [signals.comment_was_flagged])

        signals.comment_was_flagged.disconnect(receive)


class DeleteViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="moderator",
            password="test123456",
            is_staff=True,
            is_superuser=False,
        )

        self.comment = MPTTComment.objects.create(
            content_type=CT(Site),
            object_pk="1",
            user_name="Somebody",
            user_email="Somebody@example.com",
            comment="Some text",
            site=Site.objects.get_current(),
        )

    def test_delete_permissions(self):
        pk = self.comment.pk
        self.client.login(username="moderator", password="test123456")
        response = self.client.get("/delete/%d/" % pk)
        self.assertEqual(response.status_code, 403)

        make_moderator("moderator")

        response = self.client.get("/delete/%d/" % pk)
        self.assertEqual(response.status_code, 200)

    def test_delete_post(self):
        pk = self.comment.pk
        make_moderator("moderator")
        self.client.login(username="moderator", password="test123456")
        response = self.client.post("/delete/%d/" % pk)
        self.assertRedirects(response, "/deleted/?c=%d" % pk)
        c = MPTTComment.objects.get(pk=pk)
        self.assertEqual(
            c.mpttcommentflag_set.filter(flag=MPTTCommentFlag.MODERATOR_DELETION, user__username="moderator").count(),
            1
        )

    def test_delete_post_next(self):
        pk = self.comment.pk
        make_moderator("moderator")
        self.client.login(username="moderator", password="test123456")
        response = self.client.post("/delete/%d/" % pk, data={'next': '/go/here/'})
        self.assertRedirects(response, "/go/here/?c=%d" % pk, fetch_redirect_response=False)
        c = MPTTComment.objects.get(pk=pk)
        self.assertEqual(
            c.mpttcommentflag_set.filter(flag=MPTTCommentFlag.MODERATOR_DELETION, user__username="moderator").count(),
            1
        )

    def test_delete_signals(self):
        def receive(sender, **kwargs):
            received_signals.append(kwargs.get('signal'))

        # Connect signals and keep track of handled ones
        received_signals = []
        signals.comment_was_flagged.connect(receive)

        # Post a comment and check the signals
        self.test_delete_post()
        self.assertEqual(received_signals, [signals.comment_was_flagged])

        signals.comment_was_flagged.disconnect(receive)
