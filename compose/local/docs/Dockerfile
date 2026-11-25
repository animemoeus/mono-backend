FROM ghcr.io/astral-sh/uv:0.13.10 AS uv

# define an alias for the specific python version used in this file.
FROM docker.io/python:3.14.10-slim-trixie AS python


# Python build stage
FROM python AS python-build-stage

ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg dependencies
  libpq-dev \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /bin/uv

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements

# Install Python dependencies into an isolated virtual environment.
RUN --mount=type=cache,target=/root/.cache/uv \
  uv venv /opt/venv \
  && uv pip install --python /opt/venv/bin/python -r /requirements/local.txt -r /requirements/production.txt \
  && rm -rf /requirements


# Python 'run' stage
FROM python AS python-run-stage

ARG BUILD_ENVIRONMENT
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install --no-install-recommends -y \
  # To run the Makefile
  make \
  # psycopg dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # Uncomment below lines to enable Sphinx output to latex and pdf
  # texlive-latex-recommended \
  # texlive-fonts-recommended \
  # texlive-latex-extra \
  # latexmk \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# copy virtualenv from python-build-stage
COPY --from=python-build-stage /opt/venv /opt/venv

COPY ./compose/local/docs/start /start-docs
RUN sed -i 's/\r$//g' /start-docs
RUN chmod +x /start-docs

WORKDIR /docs
