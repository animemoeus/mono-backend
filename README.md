# AnimeMoeUs Backend

> A personal monorepo for testing, prototyping, and somehow also running things in production. Nobody planned this. Here we are.

[![codecov](https://codecov.io/gh/animemoeus/mono-backend/branch/master/graph/badge.svg?token=8UHQY5ZZSE)](https://codecov.io/gh/animemoeus/mono-backend)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Deployment](https://github.com/animemoeus/backend/actions/workflows/deployment.yml/badge.svg)](https://github.com/animemoeus/backend/actions/workflows/deployment.yml)
[![Uptime Robot status](https://img.shields.io/uptimerobot/status/m788586431-1256ae08e9b37721503fdef8)](https://stats.uptimerobot.com/GKy6liBGw7/788586431)
[![Uptime Robot ratio (30 days)](https://img.shields.io/uptimerobot/ratio/m788586431-1256ae08e9b37721503fdef8)](https://stats.uptimerobot.com/GKy6liBGw7/788586431)
[![GitHub Release](https://img.shields.io/github/v/release/animemoeus/backend)](https://github.com/animemoeus/backend/releases)

---

Links you will bookmark, never revisit, and forget existed:

- [📈 Uptime Robot](https://stats.uptimerobot.com/GKy6liBGw7) - for the thrill of watching a green dot that could turn red at any moment
- [🧑‍⚕️ Health Check](https://api.animemoe.us/health-check/) - it says healthy. we choose to believe it
- [👀 Admin Panel](https://api.animemoe.us/admin/) - where you go to fix things you broke from here
- [🌸 Django Flower](https://flower.animemoe.us/) - a flower that monitors your task queue. very zen. very broken sometimes
- [📊 Docker Logs](https://dozzle.unklab.id/) - a beautiful UI for reading errors you will not fix today

---

## Discord

### Refresh Expired URL

[![Uptime Robot status](https://img.shields.io/uptimerobot/status/m797080158-bcfd7f8a26110828783eff90)](https://stats.uptimerobot.com/GKy6liBGw7/797080158) [![Uptime Robot ratio (30 days)](https://img.shields.io/uptimerobot/ratio/m797080158-bcfd7f8a26110828783eff90)](https://stats.uptimerobot.com/GKy6liBGw7/797080158)

Discord expires CDN URLs after a while because apparently permanent links were too convenient. This service exists solely to work around that decision.

#### https://docs.api.animemoe.us/discord/refresh-url

---

## Twitter Downloader

Twitter/X decided downloading your own content should cost money. Respectfully, no.

### Docs: <https://docs.api.animemoe.us/twitter-downloader/twitter-video-downloader-bot>

---

## Basic Commands

Everything runs inside Docker. If you are trying to run these commands directly on your OS, close the terminal, take a breath, and come back.

### Start the Stack

```bash
docker compose -f local.yml up
```

Or in the background, if you have better things to watch than container logs scrolling forever:

```bash
docker compose -f local.yml up -d
```

### Setting Up Your Users

To create a superuser account and feel a brief moment of power:

```bash
docker compose -f local.yml exec django python manage.py createsuperuser
```

### Django Shell

For when you need to poke the database and pretend you know what you are doing:

```bash
docker compose -f local.yml exec django python manage.py shell
```

### Migrations

Made changes to a model? Great. Now do this:

```bash
docker compose -f local.yml exec django python manage.py makemigrations
docker compose -f local.yml exec django python manage.py migrate
```

### Type Checks

Running mypy because we like to pretend we write typed Python:

```bash
docker compose -f local.yml exec django mypy backend
```

### Test Coverage

Run the tests, generate a coverage report, open it once, feel good about yourself, never open it again:

```bash
docker compose -f local.yml exec django coverage run -m pytest
docker compose -f local.yml exec django coverage html
open htmlcov/index.html
```

Just pytest, no ceremony:

```bash
docker compose -f local.yml exec django pytest
```

Make sure all tests pass before pushing. Or push anyway and deal with it in CI like everyone else.

### Celery

Celery runs as its own containers (`celeryworker`, `celerybeat`) and starts automatically with the stack. You do not need to do anything unless something is broken, at which point you will be reading these logs and questioning your choices:

```bash
docker compose -f local.yml logs -f celeryworker
docker compose -f local.yml logs -f celerybeat
```

### Sentry

Sentry catches errors so you do not have to find out about them from users. Sign up at <https://sentry.io/signup/> or self-host if you enjoy managing one more service that can go down.

Set the DSN URL in production. You will only forget once.

## Deployment

### Docker

It is Docker. You know what to do. If you do not, maybe start there.
