#!/usr/bin/env python

import os
import json
import sys
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

async def make_api_request(endpoint: str, params: Dict[str, Any] = None, accept_json: bool = True) -> Dict[str, Any]:
    """Make a request to the Chess.com API"""
    url = f"{config.base_url}/{endpoint}"
    headers = {
        "accept": "application/json" if accept_json else "application/x-chess-pgn"
    }
    
    async with httpx.AsyncClient() as client:
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
    """
    Get a player's profile information from Chess.com.
    
    Parameters:
    - username: The Chess.com username
    """
    return await make_api_request(f"player/{username}")

@mcp.tool(description="Get a player's stats from Chess.com")
async def get_player_stats(
    username: str
) -> Dict[str, Any]:
    """
    Get a player's chess statistics from Chess.com.
    
    Parameters:
    - username: The Chess.com username
    """
    return await make_api_request(f"player/{username}/stats")

@mcp.tool(description="Check if a player is currently online on Chess.com")
async def is_player_online(
    username: str
) -> Dict[str, Any]:
    """
    Check if a player is currently online on Chess.com.
    
    Parameters:
    - username: The Chess.com username
    """
    return await make_api_request(f"player/{username}/is-online")

@mcp.tool(description="Get a player's ongoing games on Chess.com")
async def get_player_current_games(
    username: str
) -> Dict[str, Any]:
    """
    Get a list of a player's current games on Chess.com.
    
    Parameters:
    - username: The Chess.com username
    """
    return await make_api_request(f"player/{username}/games")

@mcp.tool(description="Get a player's games for a specific month from Chess.com")
async def get_player_games_by_month(
    username: str,
    year: int,
    month: int
) -> Dict[str, Any]:
    """
    Get a player's games for a specific month from Chess.com.
    
    Parameters:
    - username: The Chess.com username
    - year: Year (YYYY format)
    - month: Month (MM format, 01-12)
    """
    month_str = str(month).zfill(2)
    return await make_api_request(f"player/{username}/games/{year}/{month_str}")

@mcp.tool(description="Get a list of available monthly game archives for a player on Chess.com")
async def get_player_game_archives(
    username: str
) -> Dict[str, Any]:
    """
    Get a list of available monthly game archives for a player on Chess.com.
    
    Parameters:
    - username: The Chess.com username
    """
    return await make_api_request(f"player/{username}/games/archives")

@mcp.tool(description="Get a list of titled players from Chess.com")
async def get_titled_players(
    title: str
) -> Dict[str, Any]:
    """
    Get a list of titled players from Chess.com.
    
    Parameters:
    - title: Chess title (GM, WGM, IM, WIM, FM, WFM, NM, WNM, CM, WCM)
    """
    valid_titles = ["GM", "WGM", "IM", "WIM", "FM", "WFM", "NM", "WNM", "CM", "WCM"]
    if title not in valid_titles:
        raise ValueError(f"Invalid title. Must be one of: {', '.join(valid_titles)}")
    
    return await make_api_request(f"titled/{title}")

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
    url_id: str
) -> Dict[str, Any]:
    """
    Get members of a club on Chess.com.
    
    Parameters:
    - url_id: The URL identifier of the club
    """
    return await make_api_request(f"club/{url_id}/members")

@mcp.tool(description="Download PGN files for all games in a specific month from Chess.com")
async def download_player_games_pgn(
    username: str,
    year: int,
    month: int
) -> str:
    """
    Download PGN files for all games in a specific month from Chess.com.
    
    Parameters:
    - username: The Chess.com username
    - year: Year (YYYY format)
    - month: Month (MM format, 01-12)
    
    Returns:
    - Multi-game PGN format text containing all games for the month
    """
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
    """
    Resource that returns a player's current games.
    
    Parameters:
    - username: The Chess.com username
    """
    try:
        games = await get_player_current_games(username=username)
        return json.dumps(games, indent=2)
    except Exception as e:
        return f"Error retrieving current games: {str(e)}"

@mcp.resource("chess://player/{username}/games/{year}/{month}")
async def player_games_by_month_resource(username: str, year: str, month: str) -> str:
    """
    Resource that returns a player's games for a specific month.
    
    Parameters:
    - username: The Chess.com username
    - year: Year (YYYY format)
    - month: Month (MM format, 01-12)
    """
    try:
        games = await get_player_games_by_month(username=username, year=int(year), month=int(month))
        return json.dumps(games, indent=2)
    except Exception as e:
        return f"Error retrieving games by month: {str(e)}"

@mcp.resource("chess://titled/{title}")
async def titled_players_resource(title: str) -> str:
    """
    Resource that returns a list of titled players.
    
    Parameters:
    - title: Chess title (GM, WGM, IM, WIM, FM, WFM, NM, WNM, CM, WCM)
    """
    try:
        players = await get_titled_players(title=title)
        return json.dumps(players, indent=2)
    except Exception as e:
        return f"Error retrieving titled players: {str(e)}"

@mcp.resource("chess://club/{url_id}")
async def club_profile_resource(url_id: str) -> str:
    """
    Resource that returns club profile data.
    
    Parameters:
    - url_id: The URL identifier of the club
    """
    try:
        profile = await get_club_profile(url_id=url_id)
        return json.dumps(profile, indent=2)
    except Exception as e:
        return f"Error retrieving club profile: {str(e)}"

@mcp.resource("chess://player/{username}/games/{year}/{month}/pgn")
async def player_games_pgn_resource(username: str, year: str, month: str) -> str:
    """
    Resource that returns a player's games for a specific month in PGN format.
    
    Parameters:
    - username: The Chess.com username
    - year: Year (YYYY format)
    - month: Month (MM format, 01-12)
    """
    try:
        pgn_data = await download_player_games_pgn(username=username, year=int(year), month=int(month))
        return pgn_data
    except Exception as e:
        return f"Error downloading PGN data: {str(e)}"

if __name__ == "__main__":
    mcp.run()
