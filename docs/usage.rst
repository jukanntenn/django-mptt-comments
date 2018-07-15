=====
Usage
=====

To use django-mptt-comments in a project, add it to your `INSTALLED_APPS`:

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
