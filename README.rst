Cookiecutter Django Rest Framework
=======================

My cookiecutter template for django-rest-framework project. Based on `cookiecutter django`_. Very customized

Features
---------

* Django 1.10
* `Django Rest Framework`_
* Docker support using docker-compose_(not for real use, example configuration)
* 12-Factor_ based settings via django-environ
* Custom users application with email-only(without username) user model, social auth using
* Docker support using docker-compose_
* _Sentry integration
* Api docs with `Django Rest Swagger`_
* Cron management with django-cron_


.. _`cookiecutter django`: https://github.com/pydanny/cookiecutter-django
.. _docker-compose: https://github.com/docker/compose
.. _12-Factor: http://12factor.net/
.. _Sentry: https://sentry.io/welcome/
.. _`Django Rest Framework`: http://www.django-rest-framework.org/
.. _`Django Rest Swagger`: https://github.com/marcgibbons/django-rest-swagger
.. _django-cron: https://github.com/Tivix/django-cron


Usage
------

Let's pretend you want to create a Django project called "redditclone". Rather than using `startproject`
and then editing the results to include your name, email, and various configuration issues that always get forgotten until the worst possible moment, get cookiecutter_ to do all the work.

First, get Cookiecutter. Trust me, it's awesome::

    $ pip install "cookiecutter>=1.4.0"

Now run it against this repo::

    $ cookiecutter https://github.com/dimka2014/cookiecutter-django-rest

You'll be prompted for some values. Provide them, then a Django project will be created for you.
