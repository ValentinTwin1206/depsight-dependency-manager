ARG PYTHON_VERSION="3.12"
FROM mcr.microsoft.com/devcontainers/python:${PYTHON_VERSION}

# Install uv (fast Python package manager)
ARG UV_VERSION="0.11.1"
RUN curl -LsSf https://astral.sh/uv/${UV_VERSION}/install.sh \
    | UV_INSTALL_DIR=/usr/local/bin sh

# Prevent Python stdout buffering
ENV PYTHONUNBUFFERED=1

# App environment
ENV APP_NAME=DEPSIGHT
ENV DEPSIGHT_ENV=development

# MkDocs dev server port
EXPOSE 8000