# Chess.com MCP Server

A [Model Context Protocol][mcp] (MCP) server for Chess.com's Published Data API.

This provides access to Chess.com player data, game records, and other public information through standardized MCP interfaces, allowing AI assistants to search and analyze chess information.

[mcp]: https://modelcontextprotocol.io

## Features

- [x] Access player profiles, stats, and game records
- [x] Search games by date and player
- [x] Check player online status
- [x] Get information about clubs and titled players
- [x] No authentication required (uses Chess.com's public API)
- [x] Docker containerization support
- [x] Provide interactive tools for AI assistants

The list of tools is configurable, so you can choose which tools you want to make available to the MCP client.

## Usage

Add the server configuration to your client configuration file. For example, for Claude Desktop:

Copy the following configuration to your Claude Desktop configuration file at `~/.config/claude/claude-config.json`:

```json
{
  "mcpServers": {
    "chess": {
      "command": "python",
      "args": [
        "-m",
        "src.chess_mcp.main"
      ],
      "cwd": "/Users/Pavel.Shklovsky/github/chess-mcp",
      "env": {
        "PYTHONPATH": "/Users/Pavel.Shklovsky/github/chess-mcp"
      }
    }
  }
}
```

Alternatively, you can use UV for running the server:

```json
{
  "mcpServers": {
    "chess": {
      "command": "/Users/Pavel.Shklovsky/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/Pavel.Shklovsky/github/chess-mcp",
        "run",
        "src/chess_mcp/main.py"
      ],
      "env": {}
    }
  }
}
```

> Note: if you see `Error: spawn python ENOENT` in Claude Desktop, you may need to specify the full path to `python`.

## Docker Usage

This project includes Docker support for easy deployment and isolation.

### Building the Docker Image

Build the Docker image using:

```bash
docker build -t chess-mcp-server .
```

### Running with Docker

You can run the server using Docker:

```bash
docker run -it --rm chess-mcp-server
```

### Running with Docker in Claude Desktop

To use the containerized server with Claude Desktop, update the configuration to use Docker:

```json
{
  "mcpServers": {
    "chess": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "chess-mcp-server"
      ]
    }
  }
}
```

## Development

Contributions are welcome! Please open an issue or submit a pull request if you have any suggestions or improvements.

This project uses [`uv`](https://github.com/astral-sh/uv) to manage dependencies. Install `uv` following the instructions for your platform:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

You can then create a virtual environment and install the dependencies with:

```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows
uv pip install -e .
```

## Project Structure

The project has been organized with a `src` directory structure:

```
chess-mcp/
├── src/
│   └── chess_mcp/
│       ├── __init__.py      # Package initialization
│       ├── server.py        # MCP server implementation
│       ├── main.py          # Main application logic
├── Dockerfile               # Docker configuration
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

### Testing

The project includes a test suite that ensures functionality and helps prevent regressions.

Run the tests with pytest:

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run the tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing
```

### Tools

| Tool | Category | Description |
| --- | --- | --- |
| `get_player_profile` | Player | Get a player's profile from Chess.com |
| `get_player_stats` | Player | Get a player's stats from Chess.com |
| `is_player_online` | Player | Check if a player is currently online on Chess.com |
| `get_player_current_games` | Games | Get a player's ongoing games on Chess.com |
| `get_player_games_by_month` | Games | Get a player's games for a specific month from Chess.com |
| `get_player_game_archives` | Games | Get a list of available monthly game archives for a player on Chess.com |
| `get_titled_players` | Players | Get a list of titled players from Chess.com |
| `get_club_profile` | Clubs | Get information about a club on Chess.com |
| `get_club_members` | Clubs | Get members of a club on Chess.com |

## License

MIT

---

[mcp]: https://modelcontextprotocol.io
