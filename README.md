# AnimeMoeUs Backend

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![codecov](https://codecov.io/gh/animemoeus/mono-backend/branch/master/graph/badge.svg?token=8UHQY5ZZSE)](https://codecov.io/gh/animemoeus/mono-backend)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Deployment](https://github.com/animemoeus/backend/actions/workflows/deployment.yml/badge.svg)](https://github.com/animemoeus/backend/actions/workflows/deployment.yml)
[![Uptime Robot status](https://img.shields.io/uptimerobot/status/m788586431-1256ae08e9b37721503fdef8)](https://stats.uptimerobot.com/GKy6liBGw7/788586431)
[![Uptime Robot ratio (30 days)](https://img.shields.io/uptimerobot/ratio/m788586431-1256ae08e9b37721503fdef8)](https://stats.uptimerobot.com/GKy6liBGw7/788586431)
[![GitHub Release](https://img.shields.io/github/v/release/animemoeus/backend)](https://github.com/animemoeus/backend/releases)

---

- [📈 Uptime Robot](https://stats.uptimerobot.com/GKy6liBGw7)
- [🧑‍⚕️ Health Check](https://api.animemoe.us/health-check/)
- [👀 Admin Panel](https://api.animemoe.us/admin/)
- [🌸 Django Flower](https://flower.animemoe.us/)
- [📊 Docker Logs](https://dozzle.unklab.id/)

---

## Discord

### Refresh Expired URL

[![Uptime Robot status](https://img.shields.io/uptimerobot/status/m797080158-bcfd7f8a26110828783eff90)](https://stats.uptimerobot.com/GKy6liBGw7/797080158) [![Uptime Robot ratio (30 days)](https://img.shields.io/uptimerobot/ratio/m797080158-bcfd7f8a26110828783eff90)](https://stats.uptimerobot.com/GKy6liBGw7/797080158)

#### https://docs.api.animemoe.us/discord/refresh-url

---

## Twitter Downloader

### Docs: https://docs.api.animemoe.us/twitter-downloader/twitter-video-downloader-bot


---

## Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    $ mypy backend

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading).

### Celery

This app comes with Celery.

To run a celery worker:

```bash
cd backend
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important _where_ the celery commands are run. If you are in the same folder with _manage.py_, you should be right.

To run [periodic tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html), you'll need to start the celery beat scheduler service. You can start it as a standalone process:

```bash
cd backend
celery -A config.celery_app beat
```

or you can embed the beat service inside a worker with the `-B` option (not recommended for production use):

```bash
cd backend
celery -A config.celery_app worker -B -l info
```

### Sentry

Sentry is an error logging aggregator service. You can sign up for a free account at <https://sentry.io/signup/?code=cookiecutter> or download and host it yourself.
The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

## Deployment

The following details how to deploy this application.

### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).
