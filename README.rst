=============================
django-mptt-comments
=============================

.. image:: https://badge.fury.io/py/django-mptt-comments.svg
    :target: https://badge.fury.io/py/django-mptt-comments

.. image:: https://travis-ci.org/zmrenwu/django-mptt-comments.svg?branch=master
    :target: https://travis-ci.org/zmrenwu/django-mptt-comments

.. image:: https://codecov.io/gh/zmrenwu/django-mptt-comments/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/zmrenwu/django-mptt-comments

writting...

Documentation
-------------

The full documentation is at https://django-mptt-comments.readthedocs.io.

Quickstart
----------

Install django-mptt-comments::

    pip install django-mptt-comments

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_mptt_comments.apps.DjangoMpttCommentsConfig',
        ...
    )

Add django-mptt-comments's URL patterns:

.. code-block:: python

    from django_mptt_comments import urls as django_mptt_comments_urls


    urlpatterns = [
        ...
        url(r'^', include(django_mptt_comments_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
