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
    titled_players_resource, club_profile_resource, player_games_pgn_resource,
    create_cursor, parse_cursor, paginate_data
)
from chess_mcp.main import setup_environment, run_server

@pytest.mark.asyncio
async def test_make_api_request():
    # Mock the httpx client response
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test_data"}
    mock_response.raise_for_status = MagicMock()
    
    # Mock the httpx client
    mock_client = MagicMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response
    
    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await make_api_request("endpoint/test")
        
    assert result == {"data": "test_data"}
    mock_client.__aenter__.return_value.get.assert_called_once()
    url_called = mock_client.__aenter__.return_value.get.call_args[0][0]
    assert url_called == f"{config.base_url}/endpoint/test"

@pytest.mark.asyncio
async def test_get_player_profile():
    # Mock the make_api_request function
    mock_data = {"username": "testuser", "avatar": "test_url", "status": "active"}
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)):
        result = await get_player_profile("testuser")
    
    assert result == mock_data

@pytest.mark.asyncio
async def test_get_player_stats():
    # Mock the make_api_request function
    mock_data = {"chess_rapid": {"last": {"rating": 1500}}}
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)):
        result = await get_player_stats("testuser")
    
    assert result == mock_data

@pytest.mark.asyncio
async def test_is_player_online():
    # Mock the make_api_request function
    mock_data = {"online": True}
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)):
        result = await is_player_online("testuser")
    
    assert result == mock_data

@pytest.mark.asyncio
async def test_get_player_current_games():
    # Mock the make_api_request function
    mock_data = {"games": [{"url": "game_url"}]}
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)):
        result = await get_player_current_games("testuser")
    
    assert result == mock_data

@pytest.mark.asyncio
async def test_get_player_games_by_month():
    # Mock the make_api_request function
    mock_data = {"games": [{"url": "game_url", "pgn": "pgn_data"}]}
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)):
        result = await get_player_games_by_month("testuser", 2023, 12)
    
    # Updated to expect pagination structure
    assert "games" in result
    assert "pagination" in result
    assert len(result["games"]) == 1
    assert result["games"][0] == {"url": "game_url", "pgn": "pgn_data"}
    assert result["pagination"]["total_count"] == 1

@pytest.mark.asyncio
async def test_get_titled_players():
    # Mock the make_api_request function
    mock_data = {"players": ["player1", "player2"]}
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)):
        result = await get_titled_players("GM")
    
    # Updated to expect pagination structure
    assert "players" in result
    assert "pagination" in result
    assert len(result["players"]) == 2
    assert result["players"] == ["player1", "player2"]
    assert result["pagination"]["total_count"] == 2

@pytest.mark.asyncio
async def test_get_titled_players_invalid_title():
    with pytest.raises(ValueError):
        await get_titled_players("INVALID")

@pytest.mark.asyncio
async def test_get_club_profile():
    # Mock the make_api_request function
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
    # Test the make_api_request function with query parameters
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
    # Verify parameters were passed correctly
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
    # Test the specific ValueError for invalid title
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
    mock_members = {"weekly": ["member1"], "monthly": ["member2"], "all_time": []}
    
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_members)):
        result = await get_club_members("test-club")
    
    # Updated to expect pagination structure
    assert "members" in result
    assert "pagination" in result
    assert result["pagination"]["total_count"] == 2  # member1 + member2
    assert "member1" in result["members"]
    assert "member2" in result["members"]

@pytest.mark.asyncio
async def test_get_player_game_archives():
    mock_archives = {"archives": ["https://api.chess.com/pub/player/username/games/2022/01"]}
    
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_archives)):
        result = await get_player_game_archives("username")
    
    assert result == mock_archives

@pytest.mark.asyncio
async def test_make_api_request_non_json():
    # Test the make_api_request function with non-JSON response (PGN)
    mock_response = MagicMock()
    mock_response.text = "[Event \"Live Chess\"]\n[Site \"Chess.com\"]\n"
    mock_response.raise_for_status = MagicMock()
    
    mock_client = MagicMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response
    
    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await make_api_request("endpoint/test", accept_json=False)
        
    assert result == "[Event \"Live Chess\"]\n[Site \"Chess.com\"]\n"
    mock_client.__aenter__.return_value.get.assert_called_once()
    # Verify correct headers were used
    call_args = mock_client.__aenter__.return_value.get.call_args
    assert call_args[1]["headers"]["accept"] == "application/x-chess-pgn"

@pytest.mark.asyncio
async def test_download_player_games_pgn():
    # Test the download_player_games_pgn function
    mock_pgn = "[Event \"Live Chess\"]\n[Site \"Chess.com\"]\n"
    
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_pgn)) as mock_request:
        result = await download_player_games_pgn("testuser", 2023, 12)
    
    assert result == mock_pgn
    # Check if make_api_request was called with the correct path and accept_json=False
    mock_request.assert_called_once()
    call_args = mock_request.call_args
    assert call_args[0][0] == "player/testuser/games/2023/12/pgn"
    assert call_args[1]["accept_json"] is False

@pytest.mark.asyncio
async def test_player_games_pgn_resource():
    # Test the player_games_pgn_resource function
    mock_pgn = "[Event \"Live Chess\"]\n[Site \"Chess.com\"]\n"
    
    with patch("chess_mcp.server.download_player_games_pgn", new=AsyncMock(return_value=mock_pgn)):
        result = await player_games_pgn_resource("testuser", "2023", "12")
    
    assert result == mock_pgn

@pytest.mark.asyncio
async def test_player_games_pgn_resource_error():
    # Test error handling in player_games_pgn_resource
    with patch("chess_mcp.server.download_player_games_pgn", new=AsyncMock(side_effect=Exception("Test error"))):
        result = await player_games_pgn_resource("testuser", "2023", "12")
    
    assert "Error downloading PGN data: Test error" == result

def test_setup_environment():
    # Test the setup_environment function from main.py
    result = setup_environment()
    assert result is True
    
def test_run_server():
    # Mock the mcp.run method and sys.exit
    with patch("chess_mcp.server.mcp.run") as mock_run, \
         patch("chess_mcp.main.setup_environment", return_value=True):
        run_server()
        mock_run.assert_called_once_with(transport="stdio")

def test_run_server_setup_failed():
    # Test when setup fails
    with patch("chess_mcp.main.setup_environment", return_value=False), \
         patch("sys.exit") as mock_exit, \
         patch("chess_mcp.server.mcp.run"):  # Mock the mcp.run to prevent actual server start
        run_server()
        mock_exit.assert_called_once_with(1)

# Pagination utility tests
def test_create_cursor():
    cursor = create_cursor(25, 10)
    assert isinstance(cursor, str)
    assert len(cursor) > 0
    
    # Test that cursor is base64 encoded
    import base64
    try:
        decoded = base64.b64decode(cursor.encode()).decode()
        cursor_data = json.loads(decoded)
        assert cursor_data["offset"] == 25
        assert cursor_data["page_size"] == 10
    except (ValueError, json.JSONDecodeError):
        pytest.fail("Cursor should be valid base64-encoded JSON")

def test_parse_cursor():
    # Test valid cursor
    cursor = create_cursor(50, 20)
    parsed = parse_cursor(cursor)
    assert parsed["offset"] == 50
    assert parsed["page_size"] == 20
    
    # Test invalid cursor
    invalid_parsed = parse_cursor("invalid_cursor_data")
    assert invalid_parsed["offset"] == 0
    assert invalid_parsed["page_size"] == 50
    
    # Test empty cursor
    empty_parsed = parse_cursor("")
    assert empty_parsed["offset"] == 0
    assert empty_parsed["page_size"] == 50

def test_paginate_data():
    # Test data for pagination
    test_data = [f"item_{i}" for i in range(100)]
    
    # Test first page without cursor
    page1 = paginate_data(test_data, page_size=20)
    assert len(page1["data"]) == 20
    assert page1["data"][0] == "item_0"
    assert page1["data"][19] == "item_19"
    assert page1["pagination"]["total_count"] == 100
    assert page1["pagination"]["has_more"] == True
    assert page1["pagination"]["current_page"] == 1
    assert page1["pagination"]["page_size"] == 20
    assert page1["pagination"]["next_cursor"] is not None
    
    # Test second page with cursor
    cursor = page1["pagination"]["next_cursor"]
    page2 = paginate_data(test_data, cursor=cursor)
    assert len(page2["data"]) == 20
    assert page2["data"][0] == "item_20"
    assert page2["pagination"]["current_page"] == 2
    assert page2["pagination"]["has_more"] == True
    
    # Test last page
    last_cursor = create_cursor(80, 20)
    last_page = paginate_data(test_data, cursor=last_cursor)
    assert len(last_page["data"]) == 20
    assert last_page["pagination"]["has_more"] == False
    assert last_page["pagination"]["next_cursor"] is None
    
    # Test edge case: empty data
    empty_result = paginate_data([])
    assert len(empty_result["data"]) == 0
    assert empty_result["pagination"]["total_count"] == 0
    assert empty_result["pagination"]["has_more"] == False
    assert empty_result["pagination"]["next_cursor"] is None
    
    # Test edge case: data smaller than page size
    small_data = ["a", "b", "c"]
    small_result = paginate_data(small_data, page_size=10)
    assert len(small_result["data"]) == 3
    assert small_result["pagination"]["has_more"] == False
    assert small_result["pagination"]["next_cursor"] is None

@pytest.mark.asyncio
async def test_get_player_games_by_month_with_pagination():
    # Test the updated get_player_games_by_month with pagination
    mock_games = [{"url": f"game_{i}", "white": {"username": "player1"}} for i in range(50)]
    mock_data = {"games": mock_games}
    
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)):
        # Test without pagination parameters (backward compatibility)
        result = await get_player_games_by_month("testuser", 2023, 12)
        assert "games" in result
        assert "pagination" in result
        assert len(result["games"]) == 50  # Default page size
        assert result["pagination"]["total_count"] == 50
        assert result["pagination"]["current_page"] == 1
        assert result["pagination"]["has_more"] == False
        
        # Test with custom page size
        result = await get_player_games_by_month("testuser", 2023, 12, page_size=10)
        assert len(result["games"]) == 10
        assert result["pagination"]["page_size"] == 10
        assert result["pagination"]["has_more"] == True
        
        # Test with cursor
        cursor = result["pagination"]["next_cursor"]
        page2 = await get_player_games_by_month("testuser", 2023, 12, cursor=cursor)
        assert len(page2["games"]) == 10
        assert page2["pagination"]["current_page"] == 2
        
        # Test page size validation (should cap at 200)
        result = await get_player_games_by_month("testuser", 2023, 12, page_size=1000)
        assert result["pagination"]["page_size"] == 200

@pytest.mark.asyncio
async def test_get_titled_players_with_pagination():
    # Test the updated get_titled_players with pagination
    mock_players = [f"player_{i}" for i in range(100)]
    mock_data = {"players": mock_players}
    
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)):
        # Test without pagination parameters
        result = await get_titled_players("GM")
        assert "players" in result
        assert "pagination" in result
        assert len(result["players"]) == 100  # Default page size
        assert result["pagination"]["total_count"] == 100
        
        # Test with custom page size
        result = await get_titled_players("GM", page_size=25)
        assert len(result["players"]) == 25
        assert result["pagination"]["page_size"] == 25
        assert result["pagination"]["has_more"] == True
        
        # Test page size validation (should cap at 500)
        result = await get_titled_players("GM", page_size=1000)
        assert result["pagination"]["page_size"] == 500

@pytest.mark.asyncio
async def test_get_club_members_with_pagination():
    # Test the updated get_club_members with pagination
    mock_members_data = {
        "weekly": [f"weekly_member_{i}" for i in range(20)],
        "monthly": [f"monthly_member_{i}" for i in range(30)],
        "all_time": [f"alltime_member_{i}" for i in range(50)]
    }
    
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_members_data)):
        # Test normal operation
        result = await get_club_members("test-club")
        assert "members" in result
        assert "pagination" in result
        # Should combine all member types: 20 + 30 + 50 = 100
        assert result["pagination"]["total_count"] == 100
        
        # Test with pagination
        result = await get_club_members("test-club", page_size=20)
        assert len(result["members"]) == 20
        assert result["pagination"]["has_more"] == True

@pytest.mark.asyncio
async def test_get_club_members_different_response_formats():
    # Test handling of different API response formats
    
    # Test with list response
    mock_list_data = [f"member_{i}" for i in range(10)]
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_list_data)):
        result = await get_club_members("test-club")
        assert result["pagination"]["total_count"] == 10
    
    # Test with empty dict response
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value={})):
        result = await get_club_members("test-club")
        assert result["pagination"]["total_count"] == 0
    
    # Test with dict containing no standard keys
    mock_other_data = {"other_key": [f"member_{i}" for i in range(5)]}
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_other_data)):
        result = await get_club_members("test-club")
        assert result["pagination"]["total_count"] == 0

def test_pagination_integration():
    # Test end-to-end pagination flow
    test_data = [f"game_{i}" for i in range(73)]  # Odd number to test edge cases
    
    # Simulate getting all data through pagination
    all_items = []
    cursor = None
    page_size = 20
    page_count = 0
    
    while True:
        result = paginate_data(test_data, page_size=page_size, cursor=cursor)
        all_items.extend(result["data"])
        page_count += 1
        
        if not result["pagination"]["has_more"]:
            break
            
        cursor = result["pagination"]["next_cursor"]
        
        # Safety check to avoid infinite loop
        if page_count > 10:
            pytest.fail("Too many pages, possible infinite loop")
    
    # Verify we got all items
    assert len(all_items) == 73
    assert all_items == test_data
    assert page_count == 4  # 20 + 20 + 20 + 13 = 4 pages

def test_pagination_cursor_consistency():
    # Test that cursors work consistently across multiple calls
    test_data = [f"item_{i}" for i in range(50)]
    
    # Get page 1
    page1 = paginate_data(test_data, page_size=15)
    cursor1 = page1["pagination"]["next_cursor"]
    
    # Get page 2 multiple times with same cursor
    page2a = paginate_data(test_data, cursor=cursor1)
    page2b = paginate_data(test_data, cursor=cursor1)
    
    # Should be identical
    assert page2a["data"] == page2b["data"]
    assert page2a["pagination"]["current_page"] == page2b["pagination"]["current_page"]
    assert page2a["pagination"]["next_cursor"] == page2b["pagination"]["next_cursor"]

@pytest.mark.asyncio
async def test_month_formatting_in_api_calls():
    # Test that month formatting works correctly in paginated functions
    mock_data = {"games": []}
    
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)) as mock_request:
        # Test single digit month
        await get_player_games_by_month("testuser", 2023, 5)
        call_args = mock_request.call_args[0][0]
        assert "2023/05" in call_args
        
        # Test double digit month
        mock_request.reset_mock()
        await get_player_games_by_month("testuser", 2023, 12)
        call_args = mock_request.call_args[0][0]
        assert "2023/12" in call_args

@pytest.mark.asyncio 
async def test_backward_compatibility():
    # Ensure old function calls still work without pagination parameters
    mock_games = [{"url": f"game_{i}"} for i in range(10)]
    mock_data = {"games": mock_games}
    
    with patch("chess_mcp.server.make_api_request", new=AsyncMock(return_value=mock_data)):
        # Call without any pagination parameters (old behavior)
        result = await get_player_games_by_month("testuser", 2023, 12)
        
        # Should still work and include pagination metadata
        assert "games" in result
        assert "pagination" in result
        assert len(result["games"]) == 10
        assert result["pagination"]["current_page"] == 1
        assert result["pagination"]["total_count"] == 10

def test_error_handling_in_pagination():
    # Test error handling in pagination utilities
    
    # Test with None data
    result = paginate_data(None or [], page_size=10)
    assert result["pagination"]["total_count"] == 0
    
    # Test with invalid page size (should be corrected)
    test_data = ["a", "b", "c"]
    result = paginate_data(test_data, page_size=0)
    assert len(result["data"]) <= len(test_data)
    
    # Test with negative page size
    result = paginate_data(test_data, page_size=-5)
    assert len(result["data"]) <= len(test_data)
