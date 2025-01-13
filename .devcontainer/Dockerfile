FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# Install CodeCrafters CLI
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl https://codecrafters.io/install.sh | sh

# Create non-root user
RUN useradd -m -s /bin/bash appuser
USER appuser

# Add healthcheck
HEALTHCHECK --interval=60s --timeout=3s \
  CMD ps aux || exit 1