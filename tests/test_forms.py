from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sites.models import Site
from django.test import TestCase

from captcha.models import CaptchaStore
from django_mptt_comments.forms import MPTTCommentForm


class MPTTCommentFormTestCase(TestCase):
    def setUp(self):
        self.target_object = Site.objects.create(name='test', domain='test.com')
        self.auth_user = User.objects.create_user('user', 'test')
        self.anon_user = AnonymousUser()

    def test_valid_authenticated_comment_form(self):
        form = MPTTCommentForm(target_object=self.target_object, user=self.auth_user)
        str(form)  # display the form
        comment_data = {
            'comment': 'comment',
            'site_id': 1,
        }
        form_data = form.initial
        form_data.update(comment_data)

        new_form = MPTTCommentForm(target_object=self.target_object, data=form_data, user=self.auth_user)
        self.assertTrue(new_form.is_valid())
        self.assertNotIn('captcha', new_form.fields)

    def test_invalid_authenticated_comment_form(self):
        form = MPTTCommentForm(target_object=self.target_object, user=self.auth_user)
        str(form)  # display the form
        comment_data = {
            'site_id': 1,
        }
        form_data = form.initial
        form_data.update(comment_data)

        new_form = MPTTCommentForm(target_object=self.target_object, data=form_data, user=self.auth_user)
        self.assertFalse(new_form.is_valid())
        self.assertIn('comment', new_form.errors)
        self.assertNotIn('captcha', new_form.fields)

    def test_valid_anonymous_form(self):
        form = MPTTCommentForm(target_object=self.target_object, user=self.anon_user)
        str(form)  # display the form
        comment_data = {
            'name': 'user',
            'email': 'user@test.com',
            'captcha_1': CaptchaStore.objects.first().challenge,  # captcha text
            'captcha_0': form.fields['captcha'].widget._key,  # captcha hashkey
            'comment': 'comment',
            'site_id': 1,
        }
        form_data = form.initial
        form_data.update(comment_data)

        new_form = MPTTCommentForm(target_object=self.target_object, data=form_data, user=self.anon_user)
        self.assertTrue(new_form.is_valid())

    def test_invalid_anonymous_form(self):
        form = MPTTCommentForm(target_object=self.target_object, user=self.anon_user)
        str(form)  # display the form
        comment_data = {
            'captcha_1': 'wrong text',  # captcha text
            'captcha_0': form.fields['captcha'].widget._key,  # captcha hashkey
            'comment': 'comment',
            'site_id': 1,
        }
        form_data = form.initial
        form_data.update(comment_data)

        new_form = MPTTCommentForm(target_object=self.target_object, data=form_data, user=self.anon_user)
        self.assertFalse(new_form.is_valid())
        self.assertIn('name', new_form.errors)
        self.assertIn('email', new_form.errors)
        self.assertIn('captcha', new_form.errors)

    def test_root_comment_form(self):
        pass

    def test_child_comment_form(self):
        pass
