#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-mptt-comments
------------

Tests for `django-mptt-comments` models module.
"""

from django.test import TestCase

from .models import MarkedTextFieldBadSourceTestModel, MarkedTextFieldTestModel


class MarkedFieldTestCase(TestCase):
    def test_empty_source_value(self):
        m = MarkedTextFieldTestModel()
        m.save()
        m.refresh_from_db()
        self.assertEqual(m.body_html, '')

    def test_mark_source_value(self):
        m = MarkedTextFieldTestModel(body='#heading\n\n`code`**bold**')
        m.save()
        m.refresh_from_db()
        expected = \
            """
            <h1>heading</h1>
            <p>
                <code>code</code>
                <strong>bold</strong>
            </p>
            """
        self.assertHTMLEqual(m.body_html, expected)

    def test_bad_source(self):
        m = MarkedTextFieldBadSourceTestModel()
        self.assertRaises(AttributeError, m.save)

    def test_xss(self):
        m = MarkedTextFieldTestModel(body='#heading\n\n<script>alter("eval codes")</script>')
        m.save()
        m.refresh_from_db()
        expected = \
            """
            <h1>heading</h1>
            &lt;script&gt;alter("eval codes")&lt;/script&gt;
            """
        self.assertHTMLEqual(m.body_html, expected)

    def test_linkify(self):
        m = MarkedTextFieldTestModel(body='www.djangoproject.com')
        m.save()
        m.refresh_from_db()
        expected = \
            """
            <p>
                <a href="http://www.djangoproject.com" rel="nofollow">www.djangoproject.com</a>
            </p>
            """
        self.assertHTMLEqual(m.body_html, expected)


class TestDjango_mptt_comments(TestCase):

    def setUp(self):
        pass

    def test_something(self):
        pass

    def tearDown(self):
        pass
