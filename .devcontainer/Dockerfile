ARG PYTHON_VERSION
FROM mcr.microsoft.com/devcontainers/python:${PYTHON_VERSION}

# Install uv (fast Python package manager)
ARG UV_VERSION
RUN curl -LsSf https://astral.sh/uv/${UV_VERSION}/install.sh | sh \
 && mv /root/.local/bin/uv /usr/local/bin/uv \
 && mv /root/.local/bin/uvx /usr/local/bin/uvx

# Prevent Python stdout buffering
ENV PYTHONUNBUFFERED=1

# App environment
ENV APP_NAME=DEPLY
ENV DEPLY_ENV=development

# MkDocs dev server port
EXPOSE 8000

USER vscode