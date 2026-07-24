# syntax=docker/dockerfile:1

# ---- build stage: resolve and install dependencies with uv ----
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /usr/src/app

# Install dependencies first so the layer is cached across code changes.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# ---- runtime stage ----
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=. \
    PATH="/usr/src/app/.venv/bin:${PATH}"

WORKDIR /usr/src/app

COPY --from=builder /usr/src/app/.venv /usr/src/app/.venv
COPY dora_person ./dora_person
COPY newrelic ./newrelic

# Dev default. The production compose overrides this to wrap the process with
# newrelic-admin and use more workers (see compose.prod.yml).
CMD ["hypercorn", "-b", "unix:/var/tmp/hypercorn.sock", "-w", "4", "dora_person.main:app", "--reload"]
