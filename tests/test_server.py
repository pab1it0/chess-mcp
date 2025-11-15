import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import os
import sys

from chess_mcp.server import (
    make_api_request, config,
    get_player_profile, get_player_stats, is_player_online,
    get_player_current_games, get_player_games_by_month, get_player_game_archives,
    get_titled_players, get_club_profile, get_club_members, download_player_games_pgn,
    player_profile_resource, player_stats_resource,
    player_current_games_resource, player_games_by_month_resource,
    titled_players_resource, club_profile_resource, player_games_pgn_resource
)
from chess_mcp.main import setup_environment, run_server

@pytest.mark.asyncio
async def test_make_api_request():
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test_data"}
    mock_response.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await make_api_request("endpoint/test")

    assert result == {"data": "test_data"}
    mock_client.__aenter__.return_value.get.assert_called_once()
    url_called = mock_client.__aenter__.return_value.get.call_args[0][0]
    assert url_called == f"{config.base_url}/endpoint/test"

@pytest.mark.asyncio
async def test_make_api_request_http_error():
    """Test that HTTP errors are properly logged and re-raised."""
    import httpx
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPError("Test error")

    mock_client = MagicMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(httpx.HTTPError):
            await make_api_request("endpoint/test")

@pytest.mark.asyncio
async def test_get_player_profile():
    mock_data = {"username": "testuser", "avatar": "test_url", "status": "active"}
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)):
        result = await get_player_profile("testuser")

    assert result == mock_data

@pytest.mark.asyncio
async def test_get_player_stats():
    mock_data = {"chess_rapid": {"last": {"rating": 1500}}}
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)):
        result = await get_player_stats("testuser")

    assert result == mock_data

@pytest.mark.asyncio
async def test_is_player_online():
    mock_data = {"online": True}
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)):
        result = await is_player_online("testuser")

    assert result == mock_data

@pytest.mark.asyncio
async def test_get_player_current_games():
    mock_data = {"games": [{"url": "game_url"}]}
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)):
        result = await get_player_current_games("testuser")

    assert result == mock_data

@pytest.mark.asyncio
async def test_get_player_games_by_month():
    mock_data = {"games": [{"url": "game_url", "pgn": "pgn_data"}]}
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)):
        result = await get_player_games_by_month("testuser", 2023, 12)

    assert result == mock_data

@pytest.mark.asyncio
async def test_get_titled_players():
    mock_data = {"players": ["player1", "player2"]}
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)):
        result = await get_titled_players("GM")

    assert result == mock_data

@pytest.mark.asyncio
async def test_get_titled_players_invalid_title():
    with pytest.raises(ValueError):
        await get_titled_players("INVALID")

@pytest.mark.asyncio
async def test_get_club_profile():
    mock_data = {"name": "Test Club", "members_count": 10}
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)):
        result = await get_club_profile("test-club")

    assert result == mock_data

@pytest.mark.asyncio
async def test_player_profile_resource():
    mock_profile = {"username": "testuser", "avatar": "test_url"}

    with patch("chess_mcp.server.get_player_profile", new=AsyncMock(return_value=mock_profile)):
        result = await player_profile_resource("testuser")

    assert json.loads(result) == mock_profile

@pytest.mark.asyncio
async def test_player_profile_resource_error():
    with patch("chess_mcp.server.get_player_profile", new=AsyncMock(side_effect=Exception("Test error"))):
        result = await player_profile_resource("testuser")

    assert "Error retrieving player profile: Test error" == result

@pytest.mark.asyncio
async def test_player_stats_resource():
    mock_stats = {"chess_rapid": {"last": {"rating": 1500}}}

    with patch("chess_mcp.server.get_player_stats", new=AsyncMock(return_value=mock_stats)):
        result = await player_stats_resource("testuser")

    assert json.loads(result) == mock_stats

@pytest.mark.asyncio
async def test_player_stats_resource_error():
    with patch("chess_mcp.server.get_player_stats", new=AsyncMock(side_effect=Exception("Test error"))):
        result = await player_stats_resource("testuser")

    assert "Error retrieving player stats: Test error" == result

@pytest.mark.asyncio
async def test_player_current_games_resource():
    mock_games = {"games": [{"url": "game_url"}]}

    with patch("chess_mcp.server.get_player_current_games", new=AsyncMock(return_value=mock_games)):
        result = await player_current_games_resource("testuser")

    assert json.loads(result) == mock_games

@pytest.mark.asyncio
async def test_player_current_games_resource_error():
    with patch("chess_mcp.server.get_player_current_games", new=AsyncMock(side_effect=Exception("Test error"))):
        result = await player_current_games_resource("testuser")

    assert "Error retrieving current games: Test error" == result

@pytest.mark.asyncio
async def test_get_api_request_params():
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test_data"}
    mock_response.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response

    params = {"param1": "value1", "param2": "value2"}

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await make_api_request("endpoint/test", params=params)

    assert result == {"data": "test_data"}
    mock_client.__aenter__.return_value.get.assert_called_once()
    call_args = mock_client.__aenter__.return_value.get.call_args
    assert call_args[1]["params"] == params

@pytest.mark.asyncio
async def test_player_games_by_month_resource():
    mock_games = {"games": [{"url": "game_url", "pgn": "pgn_data"}]}

    with patch("chess_mcp.server.get_player_games_by_month", new=AsyncMock(return_value=mock_games)):
        result = await player_games_by_month_resource("testuser", "2023", "12")

    assert json.loads(result) == mock_games

@pytest.mark.asyncio
async def test_player_games_by_month_resource_error():
    with patch("chess_mcp.server.get_player_games_by_month", new=AsyncMock(side_effect=Exception("Test error"))):
        result = await player_games_by_month_resource("testuser", "2023", "12")

    assert "Error retrieving games by month: Test error" == result

@pytest.mark.asyncio
async def test_titled_players_resource():
    mock_players = {"players": ["player1", "player2"]}

    with patch("chess_mcp.server.get_titled_players", new=AsyncMock(return_value=mock_players)):
        result = await titled_players_resource("GM")

    assert json.loads(result) == mock_players

@pytest.mark.asyncio
async def test_titled_players_resource_error():
    with patch("chess_mcp.server.get_titled_players", new=AsyncMock(side_effect=Exception("Test error"))):
        result = await titled_players_resource("GM")

    assert "Error retrieving titled players: Test error" == result

@pytest.mark.asyncio
async def test_titled_players_resource_value_error():
    with patch("chess_mcp.server.get_titled_players", new=AsyncMock(side_effect=ValueError("Invalid title"))):
        result = await titled_players_resource("INVALID")

    assert "Error retrieving titled players: Invalid title" == result

@pytest.mark.asyncio
async def test_club_profile_resource():
    mock_profile = {"name": "Test Club", "members_count": 10}

    with patch("chess_mcp.server.get_club_profile", new=AsyncMock(return_value=mock_profile)):
        result = await club_profile_resource("test-club")

    assert json.loads(result) == mock_profile

@pytest.mark.asyncio
async def test_club_profile_resource_error():
    with patch("chess_mcp.server.get_club_profile", new=AsyncMock(side_effect=Exception("Test error"))):
        result = await club_profile_resource("test-club")

    assert "Error retrieving club profile: Test error" == result

@pytest.mark.asyncio
async def test_get_club_members():
    mock_members = {"members": ["member1", "member2"]}

    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_members)):
        result = await get_club_members("test-club")

    assert result == mock_members

@pytest.mark.asyncio
async def test_get_player_game_archives():
    mock_archives = {"archives": ["https://api.chess.com/pub/player/username/games/2022/01"]}

    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_archives)):
        result = await get_player_game_archives("username")

    assert result == mock_archives

@pytest.mark.asyncio
async def test_make_api_request_non_json():
    mock_response = MagicMock()
    mock_response.text = "[Event \"Live Chess\"]\n[Site \"Chess.com\"]\n"
    mock_response.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await make_api_request("endpoint/test", accept_json=False)

    assert result == "[Event \"Live Chess\"]\n[Site \"Chess.com\"]\n"
    mock_client.__aenter__.return_value.get.assert_called_once()
    call_args = mock_client.__aenter__.return_value.get.call_args
    assert call_args[1]["headers"]["accept"] == "application/x-chess-pgn"

@pytest.mark.asyncio
async def test_download_player_games_pgn():
    mock_pgn = "[Event \"Live Chess\"]\n[Site \"Chess.com\"]\n"

    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_pgn)) as mock_request:
        result = await download_player_games_pgn("testuser", 2023, 12)

    assert result == mock_pgn
    mock_request.assert_called_once()
    call_args = mock_request.call_args
    assert call_args[0][0] == "player/testuser/games/2023/12/pgn"
    assert call_args[1]["accept_json"] is False

@pytest.mark.asyncio
async def test_player_games_pgn_resource():
    mock_pgn = "[Event \"Live Chess\"]\n[Site \"Chess.com\"]\n"

    with patch("chess_mcp.server.download_player_games_pgn", new=AsyncMock(return_value=mock_pgn)):
        result = await player_games_pgn_resource("testuser", "2023", "12")

    assert result == mock_pgn

@pytest.mark.asyncio
async def test_player_games_pgn_resource_error():
    with patch("chess_mcp.server.download_player_games_pgn", new=AsyncMock(side_effect=Exception("Test error"))):
        result = await player_games_pgn_resource("testuser", "2023", "12")

    assert "Error downloading PGN data: Test error" == result

def test_setup_environment():
    result = setup_environment()
    assert result is True

def test_setup_environment_error():
    """Test setup_environment handles errors gracefully."""
    with patch("chess_mcp.main.load_dotenv", side_effect=Exception("Test error")):
        result = setup_environment()
        assert result is False

def test_run_server():
    with patch("chess_mcp.server.mcp.run") as mock_run, \
         patch("chess_mcp.main.setup_environment", return_value=True):
        run_server()
        mock_run.assert_called_once_with(transport="stdio")

def test_run_server_setup_failed():
    with patch("chess_mcp.main.setup_environment", return_value=False), \
         patch("sys.exit") as mock_exit, \
         patch("chess_mcp.server.mcp.run"):
        run_server()
        mock_exit.assert_called_once_with(1)

def test_run_server_keyboard_interrupt():
    """Test that KeyboardInterrupt is handled gracefully."""
    with patch("chess_mcp.main.setup_environment", return_value=True), \
         patch("chess_mcp.server.mcp.run", side_effect=KeyboardInterrupt):
        run_server()

def test_run_server_exception():
    """Test that general exceptions are handled and logged."""
    with patch("chess_mcp.main.setup_environment", return_value=True), \
         patch("chess_mcp.server.mcp.run", side_effect=Exception("Test error")), \
         patch("sys.exit") as mock_exit:
        run_server()
        mock_exit.assert_called_once_with(1)

def test_run_server_sse_transport():
    """Test running server with SSE transport."""
    with patch("chess_mcp.server.mcp.run") as mock_run, \
         patch("chess_mcp.main.setup_environment", return_value=True):
        run_server(transport="sse")
        mock_run.assert_called_once_with(transport="sse")
