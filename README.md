# Chess.com MCP Server

A [Model Context Protocol][mcp] (MCP) server for Chess.com's Published Data API.

[MCP Official Documentation](https://modelcontextprotocol.io/introduction)

This provides access to Chess.com player data, game records, and other public information through standardized MCP interfaces, allowing AI assistants to search and analyze chess information.

https://github.com/user-attachments/assets/3b33361b-b604-465c-9f6a-3699b6907757

[mcp]: https://modelcontextprotocol.io/introduction

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

### Docker (Recommended)

The easiest way to run chess-mcp with Claude Desktop is using Docker:

```json
{
  "mcpServers": {
    "chess": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "pab1it0/chess-mcp"
      ]
    }
  }
}
```

### Running with UV

Alternatively, you can run the server directly using UV. Add the server configuration to your client configuration file:

```json
{
  "mcpServers": {
    "chess": {
      "command": "uv",
      "args": [
        "--directory",
        "<full path to chess-mcp directory>",
        "run",
        "src/chess_mcp/main.py"
      ]
    }
  }
}
```

> Note: if you see `Error: spawn uv ENOENT` in Claude Desktop, you may need to specify the full path to `uv` or set the environment variable `NO_UV=1` in the configuration.

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

## Available Tools

### Player Information
- `get_player_profile` - Get a player's profile from Chess.com
- `get_player_stats` - Get a player's stats from Chess.com
- `is_player_online` - Check if a player is currently online on Chess.com
- `get_titled_players` - Get a list of titled players from Chess.com

### Games
- `get_player_current_games` - Get a player's ongoing games on Chess.com
- `get_player_games_by_month` - Get a player's games for a specific month from Chess.com
- `get_player_game_archives` - Get a list of available monthly game archives for a player on Chess.com
- `download_player_games_pgn` - Download PGN files for all games in a specific month from Chess.com

### Clubs
- `get_club_profile` - Get information about a club on Chess.com
- `get_club_members` - Get members of a club on Chess.com

## License

MIT

---

[mcp]: https://modelcontextprotocol.io