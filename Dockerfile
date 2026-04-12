#
# BUILD STAGE
# # # # # # # #
ARG PYTHON_VERSION="3.12"
FROM python:${PYTHON_VERSION} AS builder

# Copy uv binary from official image (Faster & more reliable than curl)
ARG UV_VERSION="0.11.1"
RUN curl -LsSf https://astral.sh/uv/${UV_VERSION}/install.sh \
    | UV_INSTALL_DIR=/usr/local/bin sh

WORKDIR /depsight

# Install dependencies (Cached Layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Install the actual project
COPY src/ src/
COPY README.md ./

# --no-editable ensures the code is physically moved into site-packages
RUN uv sync --frozen --no-dev --no-editable

#
# RUNTIME STAGE
# # # # # # # #
FROM python:${PYTHON_VERSION}-slim

WORKDIR /depsight

# Create non-root user
ARG USER_ID=1000
ARG USER_NAME=depsight
RUN apt-get update && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -g ${USER_ID} ${USER_NAME} && \
    useradd -u ${USER_ID} -g ${USER_NAME} -m -s /bin/bash ${USER_NAME}

# Copy the virtual environment ONLY
# Because we used --no-editable, the code lives inside this folder now.
COPY --from=builder --chown=${USER_NAME}:${USER_NAME} /depsight/.venv /depsight/.venv

# Copy uv binaries ONLY if Depsight needs to call 'uv' commands at runtime
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

# Prepare runtime directories
RUN mkdir -p /home/${USER_NAME}/.depsight/logs /home/${USER_NAME}/.depsight/data && \
    chown -R ${USER_NAME}:${USER_NAME} /home/${USER_NAME}

USER ${USER_NAME}

# Place the venv at the front of the PATH
ENV PATH="/depsight/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["depsight"]
