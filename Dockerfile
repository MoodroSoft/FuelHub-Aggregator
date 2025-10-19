FROM python:3.12.10

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PATH=/root/.cargo/bin:/root/.local/bin:$PATH

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        bash build-essential python3-dev curl \
        make gettext git libpq-dev wget \
    && pip3 install uv \
    && apt-get autoremove -y  \
    && apt-get clean -y  \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /logs

WORKDIR /var/www/app/src

# Copy dependency definitions for layer caching
COPY ./pyproject.toml ./
COPY ./uv.lock ./

# Install dependencies
RUN UV_PROJECT_ENVIRONMENT=/usr/local uv sync --frozen --no-install-project --no-cache

# Copy application code
COPY src/ /var/www/app/src
COPY tests/ /var/www/app/tests