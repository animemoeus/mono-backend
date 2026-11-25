
FROM ghcr.io/astral-sh/uv:0.13.10 AS uv

# define an alias for the specific python version used in this file.
FROM docker.io/python:3.14.10-slim-trixie AS python

# Python build stage
FROM python AS python-build-stage

ARG BUILD_ENVIRONMENT=production

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg dependencies
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /bin/uv

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements

# Install Python dependencies into an isolated virtual environment.
RUN --mount=type=cache,target=/root/.cache/uv \
  uv venv /opt/venv \
  && uv pip install --python /opt/venv/bin/python -r /requirements/${BUILD_ENVIRONMENT}.txt


# Python 'run' stage
FROM python AS python-run-stage

ARG BUILD_ENVIRONMENT=production
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV BUILD_ENV=${BUILD_ENVIRONMENT}
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR ${APP_HOME}

RUN addgroup --system django \
  && adduser --system --ingroup django django

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# copy virtualenv from python-build-stage
COPY --from=python-build-stage /opt/venv /opt/venv


COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint


COPY --chown=django:django ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
COPY --chown=django:django ./compose/production/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker


COPY --chown=django:django ./compose/production/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat


COPY --chown=django:django ./compose/production/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

# copy application code to WORKDIR
COPY --chown=django:django . ${APP_HOME}

# make django owner of the WORKDIR directory as well.
RUN chown django:django ${APP_HOME}

USER django

RUN DATABASE_URL="" \
  CELERY_BROKER_URL="" \
  DJANGO_SETTINGS_MODULE="config.settings.test" \
  python manage.py compilemessages

# Dummy env only satisfies production settings; collectstatic doesn't touch DB/Redis/Sentry.
RUN DJANGO_SETTINGS_MODULE="config.settings.production" \
  DJANGO_SECRET_KEY="build" \
  DJANGO_ADMIN_URL="build/" \
  DJANGO_ALLOWED_HOSTS="build" \
  DATABASE_URL="sqlite://:memory:" \
  CELERY_BROKER_URL="" \
  REDIS_URL="redis://localhost:6379/0" \
  SENTRY_DSN="" \
  python manage.py collectstatic --noinput

ENTRYPOINT ["/entrypoint"]
