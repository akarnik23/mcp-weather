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

# OpenWeatherMap API configuration
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "demo")
WEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"

# Undecorated functions for HTTP endpoint
def get_current_weather_http(location: str, units: str = "metric") -> str:
    """Get current weather for a specific location."""
    try:
        if WEATHER_API_KEY == "demo":
            # Return demo data
            demo_data = {
                "location": location,
                "temperature": 22,
                "feels_like": 21,
                "conditions": "Partly Cloudy",
                "humidity": 65,
                "pressure": 1013,
                "wind_speed": 12,
                "wind_direction": "NW",
                "units": units,
                "note": "This is demo data. Set WEATHER_API_KEY environment variable for real data."
            }
            return json.dumps(demo_data, indent=2)
        
        # Use real OpenWeatherMap API
        params = {
            "q": location,
            "appid": WEATHER_API_KEY,
            "units": units
        }
        
        response = httpx.get(f"{WEATHER_API_BASE}/weather", params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        weather_data = {
            "location": f"{data['name']}, {data['sys']['country']}",
            "temperature": data['main']['temp'],
            "feels_like": data['main']['feels_like'],
            "conditions": data['weather'][0]['description'],
            "humidity": data['main']['humidity'],
            "pressure": data['main']['pressure'],
            "wind_speed": data['wind']['speed'],
            "wind_direction": data['wind'].get('deg', 0),
            "units": units,
            "timestamp": data['dt']
        }
        
        return json.dumps(weather_data, indent=2)
        
    except httpx.RequestError as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

def get_forecast_http(location: str, days: int = 5, units: str = "metric") -> str:
    """Get weather forecast for a location."""
    try:
        days = min(max(days, 1), 5)  # Clamp between 1 and 5
        
        if WEATHER_API_KEY == "demo":
            # Return demo forecast data
            demo_forecast = {
                "location": location,
                "forecast": [
                    {
                        "date": "2024-01-15",
                        "temperature": 22,
                        "conditions": "Sunny",
                        "humidity": 60,
                        "wind_speed": 10
                    },
                    {
                        "date": "2024-01-16", 
                        "temperature": 24,
                        "conditions": "Partly Cloudy",
                        "humidity": 65,
                        "wind_speed": 12
                    },
                    {
                        "date": "2024-01-17",
                        "temperature": 20,
                        "conditions": "Rainy",
                        "humidity": 80,
                        "wind_speed": 15
                    }
                ],
                "units": units,
                "note": "This is demo data. Set WEATHER_API_KEY environment variable for real data."
            }
            return json.dumps(demo_forecast, indent=2)
        
        # Use real OpenWeatherMap API
        params = {
            "q": location,
            "appid": WEATHER_API_KEY,
            "units": units
        }
        
        response = httpx.get(f"{WEATHER_API_BASE}/forecast", params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        # Process forecast data (every 3 hours for 5 days)
        forecasts = []
        for item in data['list'][:days * 8]:  # 8 forecasts per day (every 3 hours)
            forecasts.append({
                "datetime": item['dt_txt'],
                "temperature": item['main']['temp'],
                "conditions": item['weather'][0]['description'],
                "humidity": item['main']['humidity'],
                "wind_speed": item['wind']['speed'],
                "wind_direction": item['wind'].get('deg', 0)
            })
        
        forecast_data = {
            "location": f"{data['city']['name']}, {data['city']['country']}",
            "forecast": forecasts,
            "units": units
        }
        
        return json.dumps(forecast_data, indent=2)
        
    except httpx.RequestError as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

def get_weather_alerts_http(location: str) -> str:
    """Get weather alerts for a location."""
    try:
        if WEATHER_API_KEY == "demo":
            # Return demo alert data
            demo_alerts = {
                "location": location,
                "alerts": [
                    {
                        "event": "Heat Advisory",
                        "description": "High temperatures expected",
                        "severity": "moderate",
                        "start": "2024-01-15T12:00:00Z",
                        "end": "2024-01-15T18:00:00Z"
                    }
                ],
                "note": "This is demo data. Set WEATHER_API_KEY environment variable for real data."
            }
            return json.dumps(demo_alerts, indent=2)
        
        # Use real OpenWeatherMap API for alerts
        params = {
            "q": location,
            "appid": WEATHER_API_KEY,
            "exclude": "minutely,hourly,daily"
        }
        
        response = httpx.get(f"{WEATHER_API_BASE}/onecall", params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        alerts = []
        for alert in data.get('alerts', []):
            alerts.append({
                "event": alert.get('event', ''),
                "description": alert.get('description', ''),
                "severity": alert.get('tags', ['unknown'])[0],
                "start": alert.get('start', 0),
                "end": alert.get('end', 0)
            })
        
        alert_data = {
            "location": location,
            "alerts": alerts
        }
        
        return json.dumps(alert_data, indent=2)
        
    except httpx.RequestError as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

@mcp.tool()
def get_current_weather(location: str, units: str = "metric") -> str:
    """Get current weather for a specific location.
    
    Args:
        location: City name or city name with country code (e.g., "London" or "London,UK")
        units: Units of measurement: metric, imperial, or standard (default: metric)
    
    Returns:
        JSON string with current weather data
    """
    return get_current_weather_http(location, units)

@mcp.tool()
def get_forecast(location: str, days: int = 5, units: str = "metric") -> str:
    """Get weather forecast for a location.
    
    Args:
        location: City name or city name with country code
        days: Number of days to forecast (default: 5, max: 5)
        units: Units of measurement: metric, imperial, or standard (default: metric)
    
    Returns:
        JSON string with forecast data
    """
    return get_forecast_http(location, days, units)

@mcp.tool()
def get_weather_alerts(location: str) -> str:
    """Get weather alerts for a location.
    
    Args:
        location: City name or city name with country code
    
    Returns:
        JSON string with weather alerts
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
                        "description": "Get current weather for a location", 
                        "inputSchema": {
                            "type": "object", 
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "City name or city name with country code (e.g., 'London' or 'London,UK')"
                                },
                                "units": {
                                    "type": "string",
                                    "description": "Units of measurement: metric, imperial, or standard",
                                    "enum": ["metric", "imperial", "standard"],
                                    "default": "metric"
                                }
                            },
                            "required": ["location"]
                        }
                    },
                    {
                        "name": "get_forecast", 
                        "description": "Get weather forecast for a location", 
                        "inputSchema": {
                            "type": "object", 
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "City name or city name with country code"
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
                                    "description": "Units of measurement: metric, imperial, or standard",
                                    "enum": ["metric", "imperial", "standard"],
                                    "default": "metric"
                                }
                            },
                            "required": ["location"]
                        }
                    },
                    {
                        "name": "get_weather_alerts", 
                        "description": "Get weather alerts for a location", 
                        "inputSchema": {
                            "type": "object", 
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "City name or city name with country code"
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
