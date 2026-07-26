# define an alias for the specific python version used in this file.
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim as python


# Python build stage
FROM python as python-build-stage

ENV PYTHONDONTWRITEBYTECODE 1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
# Keep the venv outside of /app: the (optional) docs service bind-mounts
# ./config and ./core over their /app counterparts, which would otherwise
# shadow a venv built at the default /app/.venv.
ENV UV_PROJECT_ENVIRONMENT=/venv

RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg dependencies
  libpq-dev \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependency manifests are copied first to keep this layer cached.
COPY pyproject.toml uv.lock ./

# Resolve and install dependencies (including the dev group, for Sphinx) into /venv.
RUN uv sync --frozen


# Python 'run' stage
FROM python as python-run-stage

ARG BUILD_ENVIRONMENT
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

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

# copy the virtualenv built in python-build-stage
COPY --from=python-build-stage /venv /venv
ENV PATH="/venv/bin:$PATH"

COPY ./compose/local/docs/start /start-docs
RUN sed -i 's/\r$//g' /start-docs
RUN chmod +x /start-docs

WORKDIR /docs
