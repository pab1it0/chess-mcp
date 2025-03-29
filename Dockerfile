# Use a Python image as the base for the builder stage
FROM python:3.12-slim-bookworm AS builder

# Copy uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY --from=ghcr.io/astral-sh/uv:latest /uvx /usr/local/bin/uvx

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy everything needed for installation
COPY pyproject.toml ./
COPY uv.lock ./
COPY src ./src/

# Create a virtual environment, then install dependencies and the project
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -e .

# Use slim Python image for the runtime stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Create a non-root user
RUN groupadd -r app && useradd -r -g app app

# Copy virtual environment and source code
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY pyproject.toml /app/

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app:${PYTHONPATH:-}"

# Expose the MCP server port
EXPOSE 8000

# Add a simple check to debug path issues
RUN echo "Checking installation:" && \
    ls -la /app/.venv/bin && \
    python -c "import sys; print(sys.path)"

# Run the MCP server using python module path
CMD ["python", "-m", "chess_mcp.main"]

# Image metadata
LABEL org.opencontainers.image.title="Chess.com API MCP Server" \
      org.opencontainers.image.description="Model Context Protocol server for Chess.com API integration" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.authors="Pavel Shklovsky" \
      org.opencontainers.image.source="https://github.com/Pavel.Shklovsky/chess-mcp" \
      org.opencontainers.image.licenses="MIT"