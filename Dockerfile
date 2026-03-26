# # # # # # # #
# BUILD STAGE
# # # # # # # #
ARG PYTHON_VERSION="3.12"
FROM python:${PYTHON_VERSION}-slim AS builder

# Install uv via official installer script
ARG UV_VERSION="0.11.1"
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/${UV_VERSION}/install.sh | UV_INSTALL_DIR=/usr/local/bin sh

WORKDIR /depsight

# Copy dependency config first (cache layer for dependency install)
COPY pyproject.toml uv.lock ./

# Install dependencies only (not the project itself)
RUN uv sync --frozen --no-install-project

# Copy source code
COPY src/ src/

# Install the project (reuses cached dependency layer above)
RUN uv sync --frozen

# # # # # # # #
# FINAL STAGE
# # # # # # # #
ARG PYTHON_VERSION="3.12"
FROM python:${PYTHON_VERSION}-slim

WORKDIR /depsight

# Create non-root user
ARG USER_ID=1000
ARG USER_NAME=depsight
RUN groupadd -g ${USER_ID} ${USER_NAME} && \
    useradd -u ${USER_ID} -g ${USER_NAME} -m -s /bin/bash ${USER_NAME}

# Copy uv binaries from the builder stage (no need to reinstall)
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

# Copy the virtual environment (includes the installed project + dependencies)
COPY --from=builder /depsight/.venv /depsight/.venv

# Copy only the plugin source needed at runtime
COPY --from=builder /depsight/src /depsight/src

# Prepare runtime directories for output
RUN mkdir -p /home/${USER_NAME}/.depsight/logs /home/${USER_NAME}/.depsight/data && \
    chown -R ${USER_NAME}:${USER_NAME} /depsight /home/${USER_NAME}

USER ${USER_NAME}

ENV PATH="/depsight/.venv/bin:$PATH"
ENV PYTHONPATH="/depsight/src"
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["depsight"]
