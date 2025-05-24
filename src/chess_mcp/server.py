#!/usr/bin/env python

import os
import json
import sys
import base64
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import httpx

import dotenv
from mcp.server.fastmcp import FastMCP

dotenv.load_dotenv()
mcp = FastMCP("Chess.com API MCP")

@dataclass
class ChessConfig:
    base_url: str = "https://api.chess.com/pub"

config = ChessConfig()

def create_cursor(offset: int, page_size: int) -> str:
    cursor_data = {
        "offset": offset,
        "page_size": page_size
    }
    cursor_json = json.dumps(cursor_data)
    return base64.b64encode(cursor_json.encode()).decode()

def parse_cursor(cursor: str) -> Dict[str, int]:
    try:
        cursor_json = base64.b64decode(cursor.encode()).decode()
        cursor_data = json.loads(cursor_json)
        return {
            "offset": cursor_data.get("offset", 0),
            "page_size": cursor_data.get("page_size", 50)
        }
    except (json.JSONDecodeError, KeyError, ValueError):
        return {"offset": 0, "page_size": 50}

def paginate_data(data: List[Any], page_size: int = 50, cursor: Optional[str] = None) -> Dict[str, Any]:
    if cursor:
        cursor_info = parse_cursor(cursor)
        offset = cursor_info["offset"]
        page_size = cursor_info["page_size"]
    else:
        offset = 0
    
    total_count = len(data)
    end_index = offset + page_size
    page_data = data[offset:end_index]
    
    has_more = end_index < total_count
    next_cursor = None
    if has_more:
        next_cursor = create_cursor(end_index, page_size)
    
    current_page = (offset // page_size) + 1
    
    return {
        "data": page_data,
        "pagination": {
            "next_cursor": next_cursor,
            "has_more": has_more,
            "total_count": total_count,
            "page_size": page_size,
            "current_page": current_page
        }
    }

async def make_api_request(endpoint: str, params: Dict[str, Any] = None, accept_json: bool = True) -> Dict[str, Any]:
    url = f"{config.base_url}/{endpoint}"
    headers = {
        "accept": "application/json" if accept_json else "application/x-chess-pgn"
    }
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, headers=headers, params=params or {})
        response.raise_for_status()
        if accept_json:
            return response.json()
        else:
            return response.text

@mcp.tool(description="Get a player's profile from Chess.com")
async def get_player_profile(
    username: str
) -> Dict[str, Any]:
    return await make_api_request(f"player/{username}")

@mcp.tool(description="Get a player's stats from Chess.com")
async def get_player_stats(
    username: str
) -> Dict[str, Any]:
    return await make_api_request(f"player/{username}/stats")

@mcp.tool(description="Check if a player is currently online on Chess.com")
async def is_player_online(
    username: str
) -> Dict[str, Any]:
    return await make_api_request(f"player/{username}/is-online")

@mcp.tool(description="Get a player's ongoing games on Chess.com")
async def get_player_current_games(
    username: str
) -> Dict[str, Any]:
    return await make_api_request(f"player/{username}/games")

@mcp.tool(description="Get a player's games for a specific month from Chess.com")
async def get_player_games_by_month(
    username: str,
    year: int,
    month: int,
    page_size: int = 50,
    cursor: Optional[str] = None
) -> Dict[str, Any]:
    page_size = max(1, min(page_size, 200))
    month_str = str(month).zfill(2)
    full_response = await make_api_request(f"player/{username}/games/{year}/{month_str}")
    games = full_response.get("games", [])
    paginated_result = paginate_data(games, page_size, cursor)
    
    return {
        "games": paginated_result["data"],
        "pagination": paginated_result["pagination"]
    }

@mcp.tool(description="Get a list of available monthly game archives for a player on Chess.com")
async def get_player_game_archives(
    username: str
) -> Dict[str, Any]:
    return await make_api_request(f"player/{username}/games/archives")

@mcp.tool(description="Get a list of titled players from Chess.com")
async def get_titled_players(
    title: str,
    page_size: int = 100,
    cursor: Optional[str] = None
) -> Dict[str, Any]:
    valid_titles = ["GM", "WGM", "IM", "WIM", "FM", "WFM", "NM", "WNM", "CM", "WCM"]
    if title not in valid_titles:
        raise ValueError(f"Invalid title. Must be one of: {', '.join(valid_titles)}")
    
    page_size = max(1, min(page_size, 500))
    full_response = await make_api_request(f"titled/{title}")
    players = full_response.get("players", [])
    paginated_result = paginate_data(players, page_size, cursor)
    
    return {
        "players": paginated_result["data"],
        "pagination": paginated_result["pagination"]
    }

@mcp.tool(description="Get information about a club on Chess.com")
async def get_club_profile(
    url_id: str
) -> Dict[str, Any]:
    """
    Get information about a club on Chess.com.
    
    Parameters:
    - url_id: The URL identifier of the club
    """
    return await make_api_request(f"club/{url_id}")

@mcp.tool(description="Get members of a club on Chess.com")
async def get_club_members(
    url_id: str,
    page_size: int = 100,
    cursor: Optional[str] = None
) -> Dict[str, Any]:
    page_size = max(1, min(page_size, 500))
    full_response = await make_api_request(f"club/{url_id}/members")
    
    if isinstance(full_response, dict):
        members = (full_response.get("weekly", []) + 
                  full_response.get("monthly", []) + 
                  full_response.get("all_time", []))
        if not members:
            members = full_response if isinstance(full_response, list) else []
    else:
        members = full_response if isinstance(full_response, list) else []
    
    paginated_result = paginate_data(members, page_size, cursor)
    
    return {
        "members": paginated_result["data"],
        "pagination": paginated_result["pagination"]
    }

@mcp.tool(description="Download PGN files for all games in a specific month from Chess.com")
async def download_player_games_pgn(
    username: str,
    year: int,
    month: int
) -> str:
    month_str = str(month).zfill(2)
    return await make_api_request(f"player/{username}/games/{year}/{month_str}/pgn", accept_json=False)

@mcp.resource("chess://player/{username}")
async def player_profile_resource(username: str) -> str:
    """
    Resource that returns player profile data.
    
    Parameters:
    - username: The Chess.com username
    """
    try:
        profile = await get_player_profile(username=username)
        return json.dumps(profile, indent=2)
    except Exception as e:
        return f"Error retrieving player profile: {str(e)}"

@mcp.resource("chess://player/{username}/stats")
async def player_stats_resource(username: str) -> str:
    """
    Resource that returns player statistics.
    
    Parameters:
    - username: The Chess.com username
    """
    try:
        stats = await get_player_stats(username=username)
        return json.dumps(stats, indent=2)
    except Exception as e:
        return f"Error retrieving player stats: {str(e)}"

@mcp.resource("chess://player/{username}/games/current")
async def player_current_games_resource(username: str) -> str:
    try:
        games = await get_player_current_games(username=username)
        return json.dumps(games, indent=2)
    except Exception as e:
        return f"Error retrieving current games: {str(e)}"

@mcp.resource("chess://player/{username}/games/{year}/{month}")
async def player_games_by_month_resource(username: str, year: str, month: str) -> str:
    try:
        games = await get_player_games_by_month(username=username, year=int(year), month=int(month))
        return json.dumps(games, indent=2)
    except Exception as e:
        return f"Error retrieving games by month: {str(e)}"

@mcp.resource("chess://titled/{title}")
async def titled_players_resource(title: str) -> str:
    try:
        players = await get_titled_players(title=title)
        return json.dumps(players, indent=2)
    except Exception as e:
        return f"Error retrieving titled players: {str(e)}"

@mcp.resource("chess://club/{url_id}")
async def club_profile_resource(url_id: str) -> str:
    try:
        profile = await get_club_profile(url_id=url_id)
        return json.dumps(profile, indent=2)
    except Exception as e:
        return f"Error retrieving club profile: {str(e)}"

@mcp.resource("chess://player/{username}/games/{year}/{month}/pgn")
async def player_games_pgn_resource(username: str, year: str, month: str) -> str:
    try:
        pgn_data = await download_player_games_pgn(username=username, year=int(year), month=int(month))
        return pgn_data
    except Exception as e:
        return f"Error downloading PGN data: {str(e)}"

if __name__ == "__main__":
    print(f"Starting Chess.com MCP Server...")
    mcp.run()
