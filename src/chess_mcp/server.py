#!/usr/bin/env python
"""Chess.com MCP Server - Provides tools and resources for Chess.com API integration."""

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import httpx
import structlog
from mcp.server.fastmcp import FastMCP

logger = structlog.get_logger(__name__)
mcp = FastMCP("Chess.com API MCP")


@dataclass
class ChessConfig:
    """Configuration for Chess.com API client."""

    base_url: str = "https://api.chess.com/pub"


config = ChessConfig()


async def make_api_request(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    accept_json: bool = True
) -> Union[Dict[str, Any], str]:
    """
    Make a request to the Chess.com API.

    Args:
        endpoint: The API endpoint to request
        params: Optional query parameters
        accept_json: Whether to accept JSON response (True) or PGN (False)

    Returns:
        JSON response as dict or text response as string

    Raises:
        httpx.HTTPError: If the request fails
    """
    url = f"{config.base_url}/{endpoint}"
    headers = {
        "accept": "application/json" if accept_json else "application/x-chess-pgn"
    }

    logger.debug(
        "Making API request",
        endpoint=endpoint,
        url=url,
        accept_json=accept_json,
        has_params=params is not None
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params or {})
            response.raise_for_status()

            if accept_json:
                result = response.json()
                logger.debug("API request successful", endpoint=endpoint, response_type="json")
                return result
            else:
                result = response.text
                logger.debug("API request successful", endpoint=endpoint, response_type="text")
                return result

        except httpx.HTTPError as e:
            logger.error(
                "API request failed",
                endpoint=endpoint,
                url=url,
                error=str(e),
                error_type=type(e).__name__
            )
            raise


@mcp.tool(description="Get a player's profile from Chess.com")
async def get_player_profile(username: str) -> Dict[str, Any]:
    """
    Get a player's profile information from Chess.com.

    Args:
        username: The Chess.com username

    Returns:
        Player profile data
    """
    logger.info("Fetching player profile", username=username)
    return await make_api_request(f"player/{username}")


@mcp.tool(description="Get a player's stats from Chess.com")
async def get_player_stats(username: str) -> Dict[str, Any]:
    """
    Get a player's chess statistics from Chess.com.

    Args:
        username: The Chess.com username

    Returns:
        Player statistics data
    """
    logger.info("Fetching player stats", username=username)
    return await make_api_request(f"player/{username}/stats")


@mcp.tool(description="Check if a player is currently online on Chess.com")
async def is_player_online(username: str) -> Dict[str, Any]:
    """
    Check if a player is currently online on Chess.com.

    Args:
        username: The Chess.com username

    Returns:
        Online status data
    """
    logger.info("Checking player online status", username=username)
    return await make_api_request(f"player/{username}/is-online")


@mcp.tool(description="Get a player's ongoing games on Chess.com")
async def get_player_current_games(username: str) -> Dict[str, Any]:
    """
    Get a list of a player's current games on Chess.com.

    Args:
        username: The Chess.com username

    Returns:
        Current games data
    """
    logger.info("Fetching player current games", username=username)
    return await make_api_request(f"player/{username}/games")


@mcp.tool(description="Get a player's games for a specific month from Chess.com")
async def get_player_games_by_month(
    username: str,
    year: int,
    month: int
) -> Dict[str, Any]:
    """
    Get a player's games for a specific month from Chess.com.

    Args:
        username: The Chess.com username
        year: Year (YYYY format)
        month: Month (MM format, 01-12)

    Returns:
        Games data for the specified month
    """
    month_str = str(month).zfill(2)
    logger.info(
        "Fetching player games by month",
        username=username,
        year=year,
        month=month_str
    )
    return await make_api_request(f"player/{username}/games/{year}/{month_str}")


@mcp.tool(description="Get a list of available monthly game archives for a player on Chess.com")
async def get_player_game_archives(username: str) -> Dict[str, Any]:
    """
    Get a list of available monthly game archives for a player on Chess.com.

    Args:
        username: The Chess.com username

    Returns:
        List of available game archives
    """
    logger.info("Fetching player game archives", username=username)
    return await make_api_request(f"player/{username}/games/archives")


@mcp.tool(description="Get a list of titled players from Chess.com")
async def get_titled_players(title: str) -> Dict[str, Any]:
    """
    Get a list of titled players from Chess.com.

    Args:
        title: Chess title (GM, WGM, IM, WIM, FM, WFM, NM, WNM, CM, WCM)

    Returns:
        List of titled players

    Raises:
        ValueError: If the title is not valid
    """
    valid_titles = ["GM", "WGM", "IM", "WIM", "FM", "WFM", "NM", "WNM", "CM", "WCM"]
    if title not in valid_titles:
        error_msg = f"Invalid title. Must be one of: {', '.join(valid_titles)}"
        logger.error("Invalid title provided", title=title, valid_titles=valid_titles)
        raise ValueError(error_msg)

    logger.info("Fetching titled players", title=title)
    return await make_api_request(f"titled/{title}")


@mcp.tool(description="Get information about a club on Chess.com")
async def get_club_profile(url_id: str) -> Dict[str, Any]:
    """
    Get information about a club on Chess.com.

    Args:
        url_id: The URL identifier of the club

    Returns:
        Club profile data
    """
    logger.info("Fetching club profile", url_id=url_id)
    return await make_api_request(f"club/{url_id}")


@mcp.tool(description="Get members of a club on Chess.com")
async def get_club_members(url_id: str) -> Dict[str, Any]:
    """
    Get members of a club on Chess.com.

    Args:
        url_id: The URL identifier of the club

    Returns:
        Club members data
    """
    logger.info("Fetching club members", url_id=url_id)
    return await make_api_request(f"club/{url_id}/members")


@mcp.tool(description="Download PGN files for all games in a specific month from Chess.com")
async def download_player_games_pgn(
    username: str,
    year: int,
    month: int
) -> str:
    """
    Download PGN files for all games in a specific month from Chess.com.

    Args:
        username: The Chess.com username
        year: Year (YYYY format)
        month: Month (MM format, 01-12)

    Returns:
        Multi-game PGN format text containing all games for the month
    """
    month_str = str(month).zfill(2)
    logger.info(
        "Downloading player games PGN",
        username=username,
        year=year,
        month=month_str
    )
    result = await make_api_request(
        f"player/{username}/games/{year}/{month_str}/pgn",
        accept_json=False
    )
    return result


@mcp.resource("chess://player/{username}")
async def player_profile_resource(username: str) -> str:
    """
    Resource that returns player profile data.

    Args:
        username: The Chess.com username

    Returns:
        JSON-formatted player profile
    """
    try:
        import json
        logger.debug("Fetching player profile resource", username=username)
        profile = await get_player_profile(username=username)
        return json.dumps(profile, indent=2)
    except Exception as e:
        logger.error("Error retrieving player profile", username=username, error=str(e))
        return f"Error retrieving player profile: {str(e)}"


@mcp.resource("chess://player/{username}/stats")
async def player_stats_resource(username: str) -> str:
    """
    Resource that returns player statistics.

    Args:
        username: The Chess.com username

    Returns:
        JSON-formatted player statistics
    """
    try:
        import json
        logger.debug("Fetching player stats resource", username=username)
        stats = await get_player_stats(username=username)
        return json.dumps(stats, indent=2)
    except Exception as e:
        logger.error("Error retrieving player stats", username=username, error=str(e))
        return f"Error retrieving player stats: {str(e)}"


@mcp.resource("chess://player/{username}/games/current")
async def player_current_games_resource(username: str) -> str:
    """
    Resource that returns a player's current games.

    Args:
        username: The Chess.com username

    Returns:
        JSON-formatted current games
    """
    try:
        import json
        logger.debug("Fetching player current games resource", username=username)
        games = await get_player_current_games(username=username)
        return json.dumps(games, indent=2)
    except Exception as e:
        logger.error("Error retrieving current games", username=username, error=str(e))
        return f"Error retrieving current games: {str(e)}"


@mcp.resource("chess://player/{username}/games/{year}/{month}")
async def player_games_by_month_resource(username: str, year: str, month: str) -> str:
    """
    Resource that returns a player's games for a specific month.

    Args:
        username: The Chess.com username
        year: Year (YYYY format)
        month: Month (MM format, 01-12)

    Returns:
        JSON-formatted games for the month
    """
    try:
        import json
        logger.debug(
            "Fetching player games by month resource",
            username=username,
            year=year,
            month=month
        )
        games = await get_player_games_by_month(
            username=username,
            year=int(year),
            month=int(month)
        )
        return json.dumps(games, indent=2)
    except Exception as e:
        logger.error(
            "Error retrieving games by month",
            username=username,
            year=year,
            month=month,
            error=str(e)
        )
        return f"Error retrieving games by month: {str(e)}"


@mcp.resource("chess://titled/{title}")
async def titled_players_resource(title: str) -> str:
    """
    Resource that returns a list of titled players.

    Args:
        title: Chess title (GM, WGM, IM, WIM, FM, WFM, NM, WNM, CM, WCM)

    Returns:
        JSON-formatted titled players list
    """
    try:
        import json
        logger.debug("Fetching titled players resource", title=title)
        players = await get_titled_players(title=title)
        return json.dumps(players, indent=2)
    except Exception as e:
        logger.error("Error retrieving titled players", title=title, error=str(e))
        return f"Error retrieving titled players: {str(e)}"


@mcp.resource("chess://club/{url_id}")
async def club_profile_resource(url_id: str) -> str:
    """
    Resource that returns club profile data.

    Args:
        url_id: The URL identifier of the club

    Returns:
        JSON-formatted club profile
    """
    try:
        import json
        logger.debug("Fetching club profile resource", url_id=url_id)
        profile = await get_club_profile(url_id=url_id)
        return json.dumps(profile, indent=2)
    except Exception as e:
        logger.error("Error retrieving club profile", url_id=url_id, error=str(e))
        return f"Error retrieving club profile: {str(e)}"


@mcp.resource("chess://player/{username}/games/{year}/{month}/pgn")
async def player_games_pgn_resource(username: str, year: str, month: str) -> str:
    """
    Resource that returns a player's games for a specific month in PGN format.

    Args:
        username: The Chess.com username
        year: Year (YYYY format)
        month: Month (MM format, 01-12)

    Returns:
        PGN-formatted games
    """
    try:
        logger.debug(
            "Fetching player games PGN resource",
            username=username,
            year=year,
            month=month
        )
        pgn_data = await download_player_games_pgn(
            username=username,
            year=int(year),
            month=int(month)
        )
        return pgn_data
    except Exception as e:
        logger.error(
            "Error downloading PGN data",
            username=username,
            year=year,
            month=month,
            error=str(e)
        )
        return f"Error downloading PGN data: {str(e)}"


if __name__ == "__main__":
    mcp.run()
