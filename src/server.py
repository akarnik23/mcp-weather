#!/usr/bin/env python3
"""
Weather MCP Server
A FastMCP server that provides weather data and forecasts.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
import httpx
from fastmcp import FastMCP

# Create the FastMCP server
mcp = FastMCP("Weather MCP Server")

# National Weather Service API configuration
NWS_API_BASE = "https://api.weather.gov"

def get_coordinates(location: str) -> tuple:
    """Get coordinates for a location using a simple geocoding approach."""
    # For now, return coordinates for major cities
    # In a real implementation, you'd use a geocoding service
    city_coords = {
        "new york": (40.7128, -74.0060),
        "nyc": (40.7128, -74.0060),
        "london": (51.5074, -0.1278),
        "paris": (48.8566, 2.3522),
        "tokyo": (35.6762, 139.6503),
        "los angeles": (34.0522, -118.2437),
        "chicago": (41.8781, -87.6298),
        "houston": (29.7604, -95.3698),
        "phoenix": (33.4484, -112.0740),
        "philadelphia": (39.9526, -75.1652),
        "san antonio": (29.4241, -98.4936),
        "san diego": (32.7157, -117.1611),
        "dallas": (32.7767, -96.7970),
        "san jose": (37.3382, -121.8863),
        "austin": (30.2672, -97.7431),
        "jacksonville": (30.3322, -81.6557),
        "fort worth": (32.7555, -97.3308),
        "columbus": (39.9612, -82.9988),
        "charlotte": (35.2271, -80.8431),
        "seattle": (47.6062, -122.3321),
        "denver": (39.7392, -104.9903),
        "washington": (38.9072, -77.0369),
        "boston": (42.3601, -71.0589),
        "el paso": (31.7619, -106.4850),
        "nashville": (36.1627, -86.7816),
        "detroit": (42.3314, -83.0458),
        "oklahoma city": (35.4676, -97.5164),
        "portland": (45.5152, -122.6784),
        "las vegas": (36.1699, -115.1398),
        "memphis": (35.1495, -90.0490),
        "louisville": (38.2527, -85.7585),
        "baltimore": (39.2904, -76.6122),
        "milwaukee": (43.0389, -87.9065),
        "albuquerque": (35.0844, -106.6504),
        "tucson": (32.2226, -110.9747),
        "fresno": (36.7378, -119.7871),
        "sacramento": (38.5816, -121.4944),
        "mesa": (33.4152, -111.8315),
        "kansas city": (39.0997, -94.5786),
        "atlanta": (33.7490, -84.3880),
        "long beach": (33.7701, -118.1937),
        "colorado springs": (38.8339, -104.8214),
        "raleigh": (35.7796, -78.6382),
        "miami": (25.7617, -80.1918),
        "virginia beach": (36.8529, -75.9780),
        "omaha": (41.2565, -95.9345),
        "oakland": (37.8044, -122.2712),
        "minneapolis": (44.9778, -93.2650),
        "tulsa": (36.1540, -95.9928),
        "cleveland": (41.4993, -81.6944),
        "wichita": (37.6872, -97.3301),
        "arlington": (32.7357, -97.1081)
    }
    
    location_lower = location.lower().strip()
    if location_lower in city_coords:
        return city_coords[location_lower]
    
    # Default to New York if location not found
    return (40.7128, -74.0060)

def get_weather_station(lat: float, lon: float) -> str:
    """Get the nearest weather station for given coordinates."""
    try:
        # Get the grid point for the coordinates
        response = httpx.get(f"{NWS_API_BASE}/points/{lat},{lon}", timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        # Get the observation station
        station_response = httpx.get(data["properties"]["observationStations"], timeout=10.0)
        station_response.raise_for_status()
        stations = station_response.json()
        
        # Return the first (closest) station
        if stations["features"]:
            return stations["features"][0]["properties"]["stationIdentifier"]
        
        return None
    except Exception:
        return None

# Undecorated functions for HTTP endpoint
def get_current_weather_http(location: str, units: str = "metric") -> str:
    """Get current weather for a specific location using National Weather Service API."""
    try:
        # Get coordinates for the location
        lat, lon = get_coordinates(location)
        
        # Get the grid point for the coordinates
        response = httpx.get(f"{NWS_API_BASE}/points/{lat},{lon}", timeout=10.0)
        response.raise_for_status()
        grid_data = response.json()
        
        # Get the current forecast (first period) as a fallback for current conditions
        forecast_response = httpx.get(grid_data["properties"]["forecast"], timeout=10.0)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        if not forecast_data.get("properties", {}).get("periods"):
            return json.dumps({"error": "No forecast data available for this location"}, indent=2)
        
        # Use the first forecast period as current conditions
        current_period = forecast_data["properties"]["periods"][0]
        
        # Convert temperature based on units
        temp_f = current_period.get("temperature")
        if temp_f is not None:
            if units == "metric":
                temp_c = (temp_f - 32) * 5/9
                temp = round(temp_c, 1)
                temp_unit = "°C"
            else:
                temp = temp_f
                temp_unit = "°F"
        else:
            temp = None
            temp_unit = "°C" if units == "metric" else "°F"
        
        weather_data = {
            "location": location.title(),
            "temperature": temp,
            "temperature_unit": temp_unit,
            "conditions": current_period.get("shortForecast", "Unknown"),
            "detailed_forecast": current_period.get("detailedForecast", ""),
            "wind_speed": current_period.get("windSpeed", ""),
            "wind_direction": current_period.get("windDirection", ""),
            "humidity": current_period.get("relativeHumidity", {}).get("value") if current_period.get("relativeHumidity") else None,
            "precipitation_chance": current_period.get("probabilityOfPrecipitation", {}).get("value") if current_period.get("probabilityOfPrecipitation") else None,
            "start_time": current_period.get("startTime", ""),
            "end_time": current_period.get("endTime", ""),
            "source": "National Weather Service",
            "note": "Current conditions based on forecast data"
        }
        
        return json.dumps(weather_data, indent=2)
        
    except httpx.RequestError as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

def get_forecast_http(location: str, days: int = 5, units: str = "metric") -> str:
    """Get weather forecast for a location using National Weather Service API."""
    try:
        days = min(max(days, 1), 5)  # Clamp between 1 and 5
        
        # Get coordinates for the location
        lat, lon = get_coordinates(location)
        
        # Get the grid point for the coordinates
        response = httpx.get(f"{NWS_API_BASE}/points/{lat},{lon}", timeout=10.0)
        response.raise_for_status()
        grid_data = response.json()
        
        # Get the forecast
        forecast_response = httpx.get(grid_data["properties"]["forecast"], timeout=10.0)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        forecasts = []
        for period in forecast_data["properties"]["periods"][:days * 2]:  # 2 periods per day (day/night)
            # Convert temperature based on units
            temp_f = period.get("temperature")
            if temp_f is not None:
                if units == "metric":
                    temp_c = (temp_f - 32) * 5/9
                    temp = round(temp_c, 1)
                    temp_unit = "°C"
                else:
                    temp = temp_f
                    temp_unit = "°F"
            else:
                temp = None
                temp_unit = "°C" if units == "metric" else "°F"
            
            forecasts.append({
                "name": period.get("name", ""),
                "start_time": period.get("startTime", ""),
                "end_time": period.get("endTime", ""),
                "temperature": temp,
                "temperature_unit": temp_unit,
                "conditions": period.get("shortForecast", ""),
                "detailed_forecast": period.get("detailedForecast", ""),
                "wind_speed": period.get("windSpeed", ""),
                "wind_direction": period.get("windDirection", ""),
                "humidity": period.get("relativeHumidity", {}).get("value") if period.get("relativeHumidity") else None,
                "precipitation_chance": period.get("probabilityOfPrecipitation", {}).get("value") if period.get("probabilityOfPrecipitation") else None
            })
        
        forecast_result = {
            "location": location.title(),
            "forecast": forecasts,
            "units": units,
            "source": "National Weather Service",
            "updated": forecast_data.get("properties", {}).get("updated", "")
        }
        
        return json.dumps(forecast_result, indent=2)
        
    except httpx.RequestError as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

def get_weather_alerts_http(location: str) -> str:
    """Get weather alerts for a location using National Weather Service API."""
    try:
        # Get coordinates for the location
        lat, lon = get_coordinates(location)
        
        # Get alerts for the area using the direct alerts endpoint
        alerts_response = httpx.get(f"{NWS_API_BASE}/alerts?point={lat},{lon}", timeout=10.0)
        alerts_response.raise_for_status()
        alerts_data = alerts_response.json()
        
        alerts = []
        for alert in alerts_data.get("features", []):
            properties = alert.get("properties", {})
            alerts.append({
                "event": properties.get("event", ""),
                "headline": properties.get("headline", ""),
                "description": properties.get("description", ""),
                "instruction": properties.get("instruction", ""),
                "severity": properties.get("severity", ""),
                "urgency": properties.get("urgency", ""),
                "certainty": properties.get("certainty", ""),
                "area_desc": properties.get("areaDesc", ""),
                "effective": properties.get("effective", ""),
                "expires": properties.get("expires", ""),
                "sender": properties.get("senderName", ""),
                "sender_short": properties.get("sender", "")
            })
        
        alert_result = {
            "location": location.title(),
            "alerts": alerts,
            "count": len(alerts),
            "source": "National Weather Service",
            "updated": alerts_data.get("updated", "")
        }
        
        return json.dumps(alert_result, indent=2)
        
    except httpx.RequestError as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

@mcp.tool()
def get_current_weather(location: str, units: str = "metric") -> str:
    """Get current weather for a specific location using National Weather Service data.
    
    Args:
        location: City name (e.g., "New York", "Los Angeles", "Chicago")
        units: Units of measurement: metric or imperial (default: metric)
    
    Returns:
        JSON string with current weather data from National Weather Service
    """
    return get_current_weather_http(location, units)

@mcp.tool()
def get_forecast(location: str, days: int = 5, units: str = "metric") -> str:
    """Get weather forecast for a location using National Weather Service data.
    
    Args:
        location: City name (e.g., "New York", "Los Angeles", "Chicago")
        days: Number of days to forecast (default: 5, max: 5)
        units: Units of measurement: metric or imperial (default: metric)
    
    Returns:
        JSON string with detailed forecast data from National Weather Service
    """
    return get_forecast_http(location, days, units)

@mcp.tool()
def get_weather_alerts(location: str) -> str:
    """Get weather alerts for a location using National Weather Service data.
    
    Args:
        location: City name (e.g., "New York", "Los Angeles", "Chicago")
    
    Returns:
        JSON string with official weather alerts from National Weather Service
    """
    return get_weather_alerts_http(location)

if __name__ == "__main__":
    # Run in HTTP mode for testing
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    import json
    
    # Create FastAPI app
    app = FastAPI()
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def health_check():
        return {"status": "ok", "server": "Weather MCP Server"}
    
    @app.post("/")
    @app.post("/mcp")
    async def mcp_endpoint(request: dict):
        """Handle MCP requests via HTTP POST"""
        try:
            print(f"Received request: {request}")
            
            if request.get("method") == "initialize":
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "Weather MCP Server", "version": "1.0.0"}
                    }
                })
            elif request.get("method") == "tools/list":
                tools = [
                    {
                        "name": "get_current_weather", 
                        "description": "Get current weather for a location using National Weather Service data", 
                        "inputSchema": {
                            "type": "object", 
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "City name (e.g., 'New York', 'Los Angeles', 'Chicago')"
                                },
                                "units": {
                                    "type": "string",
                                    "description": "Units of measurement: metric or imperial",
                                    "enum": ["metric", "imperial"],
                                    "default": "metric"
                                }
                            },
                            "required": ["location"]
                        }
                    },
                    {
                        "name": "get_forecast", 
                        "description": "Get weather forecast for a location using National Weather Service data", 
                        "inputSchema": {
                            "type": "object", 
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "City name (e.g., 'New York', 'Los Angeles', 'Chicago')"
                                },
                                "days": {
                                    "type": "integer",
                                    "description": "Number of days to forecast (1-5)",
                                    "minimum": 1,
                                    "maximum": 5,
                                    "default": 5
                                },
                                "units": {
                                    "type": "string",
                                    "description": "Units of measurement: metric or imperial",
                                    "enum": ["metric", "imperial"],
                                    "default": "metric"
                                }
                            },
                            "required": ["location"]
                        }
                    },
                    {
                        "name": "get_weather_alerts", 
                        "description": "Get weather alerts for a location using National Weather Service data", 
                        "inputSchema": {
                            "type": "object", 
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "City name (e.g., 'New York', 'Los Angeles', 'Chicago')"
                                }
                            },
                            "required": ["location"]
                        }
                    }
                ]
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"tools": tools}
                })
            elif request.get("method") == "tools/call":
                tool_name = request.get("params", {}).get("name")
                tool_args = request.get("params", {}).get("arguments", {})
                
                if tool_name == "get_current_weather":
                    result = get_current_weather_http(**tool_args)
                elif tool_name == "get_forecast":
                    result = get_forecast_http(**tool_args)
                elif tool_name == "get_weather_alerts":
                    result = get_weather_alerts_http(**tool_args)
                else:
                    return JSONResponse(content={
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
                    })
                
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": result}]}
                })
            else:
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": f"Method '{request.get('method')}' not found"}
                })
                
        except Exception as e:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                }, 
                status_code=500
            )
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
