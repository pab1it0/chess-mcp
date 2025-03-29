# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Copy only dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Copy the rest of the source code
COPY . .

# Install the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Create a non-root user
RUN groupadd -r app && useradd -r -g app app

# Use a slim Python image for the final stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Create a non-root user with the same UID/GID as in the builder stage
RUN groupadd -r app && useradd -r -g app app

# Copy virtual environment from builder stage
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Copy source code (only what's needed for runtime)
COPY --from=builder --chown=app:app /app/src /app/src

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER app

# Expose the default MCP server port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the MCP server when container starts
ENTRYPOINT ["chess-mcp"]

# Label the image with metadata
LABEL org.opencontainers.image.title="Chess.com API MCP Server" \
      org.opencontainers.image.description="Model Context Protocol server for Chess.com API integration" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.authors="Pavel Shklovsky" \
      org.opencontainers.image.source="https://github.com/Pavel.Shklovsky/chess-mcp" \
      org.opencontainers.image.licenses="MIT"