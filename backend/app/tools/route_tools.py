"""MCP Tools for route calculation."""

import httpx
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def calculate_route_tool(
    start_lat: float, start_lon: float, end_lat: float, end_lon: float
) -> dict[str, Any]:
    """Calculate a route between two coordinates using the Vector8 API.

    This is an MCP tool that can be called by the AI assistant to calculate
    optimal routes between any two geographical points.

    Args:
        start_lat: Starting latitude (must be between -90 and 90)
        start_lon: Starting longitude (must be between -180 and 180)
        end_lat: Ending latitude (must be between -90 and 90)
        end_lon: Ending longitude (must be between -180 and 180)

    Returns:
        A dictionary containing:
        - distance_meters: Distance of the route in meters
        - duration_seconds: Estimated travel time in seconds
        - distance_km: Distance in kilometers
        - duration_minutes: Duration in minutes
        - duration_hours: Duration in hours
        - created_at: Timestamp of when the route was created

    Raises:
        ValueError: If coordinates are invalid
        httpx.RequestError: If the API request fails
    """
    # Validate coordinates
    if not (-90 <= start_lat <= 90) or not (-180 <= start_lon <= 180):
        raise ValueError(f"Invalid start coordinates: ({start_lat}, {start_lon})")
    if not (-90 <= end_lat <= 90) or not (-180 <= end_lon <= 180):
        raise ValueError(f"Invalid end coordinates: ({end_lat}, {end_lon})")

    try:
        # Call the Vector8 API to calculate the route
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/routes/",
                json={
                    "start_lat": start_lat,
                    "start_lon": start_lon,
                    "end_lat": end_lat,
                    "end_lon": end_lon,
                },
                timeout=30.0,
            )
            response.raise_for_status()

        route_data = response.json()

        # Extract relevant data for AI response
        distance_km: float = route_data.get("distance_meters", 0) / 1000
        duration_minutes: float = route_data.get("duration_seconds", 0) / 60
        duration_hours: float = route_data.get("duration_seconds", 0) / 3600

        result = {
            "distance_meters": route_data.get("distance_meters", 0),
            "duration_seconds": route_data.get("duration_seconds", 0),
            "distance_km": distance_km,
            "duration_minutes": duration_minutes,
            "duration_hours": duration_hours,
            "created_at": route_data.get("created_at"),
        }

        logger.info(
            f"Route calculated successfully: {distance_km:.2f} km in {duration_minutes:.2f} minutes"
        )

        return result

    except httpx.RequestError as e:
        logger.error(f"Failed to calculate route: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during route calculation: {e}")
        raise


def get_calculate_route_tool_schema() -> dict[str, Any]:
    """Get the schema for the calculate_route_tool function for OpenAI.

    Returns:
        A dictionary describing the tool for use with OpenAI's function calling.
    """
    return {
        "type": "function",
        "function": {
            "name": "calculate_route",
            "description": "Calculate an optimal route between two geographic coordinates and get distance and duration information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_lat": {
                        "type": "number",
                        "description": "Starting latitude (between -90 and 90)",
                    },
                    "start_lon": {
                        "type": "number",
                        "description": "Starting longitude (between -180 and 180)",
                    },
                    "end_lat": {
                        "type": "number",
                        "description": "Ending latitude (between -90 and 90)",
                    },
                    "end_lon": {
                        "type": "number",
                        "description": "Ending longitude (between -180 and 180)",
                    },
                },
                "required": ["start_lat", "start_lon", "end_lat", "end_lon"],
            },
        },
    }


def convert_tools_to_groq_format(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert OpenAI-format tools to Groq-format tools.

    Groq API expects tools with the name field at the top level.
    Reference: Groq API expects {"type": "function", "function": {...}} format.

    Args:
        tools: List of tools in OpenAI format

    Returns:
        List of tools in proper Groq format
    """
    groq_tools = []
    for tool in tools:
        logger.debug(f"Processing tool: {tool}")

        if tool.get("type") == "function" and "function" in tool:
            function = tool["function"]

            # Extract the name from the function object
            tool_name = function.get("name")
            if not tool_name:
                logger.error(f"Tool function missing 'name' field: {function}")
                continue

            # Create the Groq-formatted tool
            # Groq expects: {"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}
            groq_tool = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": function.get("description", ""),
                    "parameters": function.get("parameters", {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    }),
                },
            }

            groq_tools.append(groq_tool)
            logger.info(f"Successfully converted tool: {tool_name}")
        else:
            logger.warning(f"Tool does not have expected structure: {tool}")

    return groq_tools


