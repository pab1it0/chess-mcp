# Use a Python image as the base for the builder stage
FROM python:3.12-slim-bookworm AS builder

# Copy uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /usr/local/bin/uv /usr/local/bin/uv

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies and package using uv sync
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy source code
COPY . .

# Install the project using uv (not in editable mode for production)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Use slim Python image for the runtime stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Create a non-root user
RUN groupadd -r app && useradd -r -g app app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy only necessary source files
COPY --from=builder /app/src /app/src

# Configure environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose the MCP server port
EXPOSE 8000

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the MCP server using python module path
CMD ["python", "-m", "chess_mcp.main"]

# Image metadata
LABEL org.opencontainers.image.title="Chess.com API MCP Server" \
      org.opencontainers.image.description="Model Context Protocol server for Chess.com API integration" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.authors="Pavel Shklovsky" \
      org.opencontainers.image.source="https://github.com/Pavel.Shklovsky/chess-mcp" \
      org.opencontainers.image.licenses="MIT"