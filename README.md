# Chess.com MCP Server

A [Model Context Protocol][mcp] (MCP) server for Chess.com's Published Data API.

This provides access to Chess.com player data, game records, and other public information through standardized MCP interfaces, allowing AI assistants to search and analyze chess information.

https://github.com/user-attachments/assets/3b33361b-b604-465c-9f6a-3699b6907757

[mcp]: https://modelcontextprotocol.io/introduction/introduction

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

The easiest way to run chess-mcp with [Claude Desktop](https://claude.ai/desktop) is using Docker. If you don't have Docker installed, you can get it from [Docker's official website](https://www.docker.com/get-started/).


Edit your Claude Desktop config file:
* Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
* Windows: `%APPDATA%/Claude/claude_desktop_config.json`
* Linux: `~/.config/Claude/claude_desktop_config.json`

Then add the following configuration:

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

Alternatively, you can run the server directly using UV. Edit your Claude Desktop config file (locations listed above) and add the server configuration:

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

> Note: if you see `Error: spawn uv ENOENT` in [Claude Desktop](https://claude.ai/desktop), you may need to specify the full path to `uv` or set the environment variable `NO_UV=1` in the configuration.

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

## Pagination Support

To handle large datasets efficiently and avoid token limit issues, several tools support pagination:

### Paginated Tools
- `get_player_games_by_month` - Supports pagination with `page_size` and `cursor` parameters
- `get_titled_players` - Supports pagination with `page_size` and `cursor` parameters  
- `get_club_members` - Supports pagination with `page_size` and `cursor` parameters

### How to Use Pagination

Each paginated tool accepts optional parameters:
- `page_size` (optional): Number of items per page (default varies by tool, maximum enforced)
- `cursor` (optional): Pagination cursor for retrieving subsequent pages

### Example Usage

```python
# Get first page of games (default page size)
response = await get_player_games_by_month("username", 2024, 12)

# Get specific page size
response = await get_player_games_by_month("username", 2024, 12, page_size=25)

# Get next page using cursor from previous response
next_cursor = response["pagination"]["next_cursor"]
if next_cursor:
    next_page = await get_player_games_by_month("username", 2024, 12, cursor=next_cursor)
```

### Response Format

Paginated responses include both data and pagination metadata:

```json
{
  "games": [...],  // or "players", "members" depending on the tool
  "pagination": {
    "next_cursor": "eyJ...",  // Base64 cursor for next page, null if no more pages
    "has_more": true,         // Boolean indicating if more pages exist
    "total_count": 156,       // Total number of items available
    "page_size": 50,          // Current page size
    "current_page": 1         // Current page number
  }
}
```

The pagination uses opaque, base64-encoded cursors that should be treated as tokens. Do not attempt to parse or modify cursors manually.

## License

MIT

---

[mcp]: https://modelcontextprotocol.io