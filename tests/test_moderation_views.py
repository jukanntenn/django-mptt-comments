from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from django_comments import signals
from django_mptt_comments.models import MPTTComment, MPTTCommentFlag

CT = ContentType.objects.get_for_model


class FlagViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="test123456",
            is_staff=False,
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

    def test_flag_get(self):
        pk = self.comment.pk
        self.client.login(username="testuser", password="test123456")
        response = self.client.get("/flag/%d/" % pk)
        self.assertTemplateUsed(response, "django_mptt_comments/flag.html")

    def test_flag_post(self):
        pk = self.comment.pk
        self.client.login(username="testuser", password="test123456")
        response = self.client.post("/flag/%d/" % pk)
        self.assertRedirects(response, "/flagged/?c=%d" % pk)
        c = MPTTComment.objects.get(pk=pk)
        self.assertEqual(c.mpttcommentflag_set.filter(flag=MPTTCommentFlag.SUGGEST_REMOVAL).count(), 1)
        return c

    def test_flag_post_next(self):
        pk = self.comment.pk
        self.client.login(username="testuser", password="test123456")
        response = self.client.post("/flag/%d/" % pk, {'next': "/go/here/"})
        self.assertRedirects(response, "/go/here/?c=%d" % pk, fetch_redirect_response=False)

    def test_flag_post_twice(self):
        c = self.test_flag_post()
        self.client.post("/flag/%d/" % c.pk)
        self.client.post("/flag/%d/" % c.pk)
        self.assertEqual(c.mpttcommentflag_set.filter(flag=MPTTCommentFlag.SUGGEST_REMOVAL).count(), 1)

    def test_flag_anonymous(self):
        pk = self.comment.pk
        response = self.client.get("/flag/%d/" % pk)
        self.assertRedirects(response,
                             "/accounts/login/?next=/flag/%d/" % pk,
                             fetch_redirect_response=False)
        response = self.client.post("/flag/%d/" % pk)
        self.assertRedirects(response,
                             "/accounts/login/?next=/flag/%d/" % pk,
                             fetch_redirect_response=False)

    def test_flagged_view(self):
        pk = self.comment.pk
        response = self.client.get("/flagged/", data={"c": pk})
        self.assertTemplateUsed(response, "django_mptt_comments/flagged.html")

    def test_flag_signals(self):
        # callback
        def receive(sender, **kwargs):
            self.assertEqual(kwargs['flag'].flag, MPTTCommentFlag.SUGGEST_REMOVAL)
            self.assertEqual(kwargs['request'].user.username, "testuser")
            received_signals.append(kwargs.get('signal'))

        # Connect signals and keep track of handled ones
        received_signals = []
        signals.comment_was_flagged.connect(receive)

        # Post a comment and check the signals
        self.test_flag_post()
        self.assertEqual(received_signals, [signals.comment_was_flagged])

        signals.comment_was_flagged.disconnect(receive)


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


class LikeViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="test123456",
            is_staff=False,
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

    def test_like_get(self):
        pk = self.comment.pk
        self.client.login(username="testuser", password="test123456")
        response = self.client.get("/like/%d/" % pk)
        self.assertTemplateUsed(response, "django_mptt_comments/like.html")

    def test_like(self):
        pk = self.comment.pk
        self.client.login(username="testuser", password="test123456")
        response = self.client.post("/like/%d/" % pk)
        self.assertRedirects(response, "/liked/?c=%d" % pk)
        c = MPTTComment.objects.get(pk=pk)
        self.assertEqual(c.mpttcommentflag_set.filter(flag=MPTTCommentFlag.LIKE).count(), 1)
        return c

    def test_cancel_like(self):
        self.client.login(username="testuser", password="test123456")
        c = self.test_like()
        response = self.client.post("/like/%d/" % c.pk)
        self.assertEqual(c.mpttcommentflag_set.filter(flag=MPTTCommentFlag.LIKE).count(), 0)

    def test_like_already_dislike(self):
        mpttcomment_flag = MPTTCommentFlag.objects.create(
            comment=self.comment,
            user=self.user,
            flag=MPTTCommentFlag.DISLIKE,
        )
        self.client.login(username="testuser", password="test123456")
        c = self.test_like()
        self.assertEqual(c.mpttcommentflag_set.filter(flag=MPTTCommentFlag.DISLIKE).count(), 0)

    def test_like_next(self):
        pk = self.comment.pk
        self.client.login(username="testuser", password="test123456")
        response = self.client.post("/like/%d/" % pk, {'next': "/go/here/"})
        self.assertRedirects(response, "/go/here/?c=%d" % pk, fetch_redirect_response=False)

    def test_like_anonymous(self):
        pk = self.comment.pk
        response = self.client.get("/like/%d/" % pk)
        self.assertRedirects(response,
                             "/accounts/login/?next=/like/%d/" % pk,
                             fetch_redirect_response=False)
        response = self.client.post("/like/%d/" % pk)
        self.assertRedirects(response,
                             "/accounts/login/?next=/like/%d/" % pk,
                             fetch_redirect_response=False)

    def test_liked_view(self):
        pk = self.comment.pk
        response = self.client.get("/liked/", data={"c": pk})
        self.assertTemplateUsed(response, "django_mptt_comments/liked.html")

    def test_like_signals(self):
        # callback
        def receive(sender, **kwargs):
            self.assertEqual(kwargs['flag'].flag, MPTTCommentFlag.LIKE)
            self.assertEqual(kwargs['request'].user.username, "testuser")
            received_signals.append(kwargs.get('signal'))

        # Connect signals and keep track of handled ones
        received_signals = []
        signals.comment_was_flagged.connect(receive)

        # Post a comment and check the signals
        self.test_like()
        self.assertEqual(received_signals, [signals.comment_was_flagged])

        signals.comment_was_flagged.disconnect(receive)


class DislikeViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="test123456",
            is_staff=False,
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

    def test_dislike_get(self):
        pk = self.comment.pk
        self.client.login(username="testuser", password="test123456")
        response = self.client.get("/dislike/%d/" % pk)
        self.assertTemplateUsed(response, "django_mptt_comments/dislike.html")

    def test_dislike(self):
        pk = self.comment.pk
        self.client.login(username="testuser", password="test123456")
        response = self.client.post("/dislike/%d/" % pk)
        self.assertRedirects(response, "/disliked/?c=%d" % pk)
        c = MPTTComment.objects.get(pk=pk)
        self.assertEqual(c.mpttcommentflag_set.filter(flag=MPTTCommentFlag.DISLIKE).count(), 1)
        return c

    def test_cancel_dislike(self):
        self.client.login(username="testuser", password="test123456")
        c = self.test_dislike()
        response = self.client.post("/dislike/%d/" % c.pk)
        self.assertEqual(c.mpttcommentflag_set.filter(flag=MPTTCommentFlag.DISLIKE).count(), 0)

    def test_dislike_already_like(self):
        mpttcomment_flag = MPTTCommentFlag.objects.create(
            comment=self.comment,
            user=self.user,
            flag=MPTTCommentFlag.LIKE,
        )
        self.client.login(username="testuser", password="test123456")
        c = self.test_dislike()
        self.assertEqual(c.mpttcommentflag_set.filter(flag=MPTTCommentFlag.LIKE).count(), 0)

    def test_dislike_next(self):
        pk = self.comment.pk
        self.client.login(username="testuser", password="test123456")
        response = self.client.post("/dislike/%d/" % pk, {'next': "/go/here/"})
        self.assertRedirects(response, "/go/here/?c=%d" % pk, fetch_redirect_response=False)

    def test_dislike_anonymous(self):
        pk = self.comment.pk
        response = self.client.get("/dislike/%d/" % pk)
        self.assertRedirects(response,
                             "/accounts/login/?next=/dislike/%d/" % pk,
                             fetch_redirect_response=False)
        response = self.client.post("/dislike/%d/" % pk)
        self.assertRedirects(response,
                             "/accounts/login/?next=/dislike/%d/" % pk,
                             fetch_redirect_response=False)

    def test_disliked_view(self):
        pk = self.comment.pk
        response = self.client.get("/disliked/", data={"c": pk})
        self.assertTemplateUsed(response, "django_mptt_comments/disliked.html")

    def test_dislike_signals(self):
        # callback
        def receive(sender, **kwargs):
            self.assertEqual(kwargs['flag'].flag, MPTTCommentFlag.DISLIKE)
            self.assertEqual(kwargs['request'].user.username, "testuser")
            received_signals.append(kwargs.get('signal'))

        # Connect signals and keep track of handled ones
        received_signals = []
        signals.comment_was_flagged.connect(receive)

        # Post a comment and check the signals
        self.test_dislike()
        self.assertEqual(received_signals, [signals.comment_was_flagged])

        signals.comment_was_flagged.disconnect(receive)
