# Weather MCP Server

A FastMCP server that provides weather data, forecasts, and alerts for Poke integration.

## 🚀 Features

- **get_current_weather**: Current conditions (from National Weather Service forecast data)
- **get_forecast**: Detailed multi-day forecast (day/night periods)
- **get_weather_alerts**: Real-time alerts and warnings (NWS official alerts)

Data Source: National Weather Service (`https://api.weather.gov`) — no API key required.

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python src/server.py
```

## 🔑 API Key Setup

Not required. This server uses the National Weather Service API and does not need an API key.

## 🚢 Deployment

### Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

**Steps:**
1. **Click the "Deploy to Render" button above** or go to [render.com](https://render.com)
2. **Connect your GitHub account to Render** (if you haven't already)
3. **Create a new Web Service:**
   - Connect this repository
   - **Name**: `weather-mcp`
   - **Environment**: `Python 3`
   - **Plan**: `Free`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/server.py`
4. No environment variables required
5. **Deploy!**

> Note: On Render's free tier, services go idle after ~15 minutes of inactivity and may require a manual "Deploy" to wake or to pick up the latest commit. Unlike Vercel, pushes do not auto-deploy by default.

Your server will be available at `https://weather-mcp.onrender.com/mcp`

## 🎯 Poke Integration

1. Go to [poke.com/settings/connections](https://poke.com/settings/connections)
2. Add the MCP URL: `https://weather-mcp.onrender.com/mcp`
3. Give it a name like "Weather"
4. Try: "Use the Weather MCP to get the 3-day forecast for Boston."

## References

- Based on the Interaction MCP server template: [MCP Server Template](https://github.com/InteractionCo/mcp-server-template/tree/main)
- Discovered via Interaction’s HackMIT challenge: [Interaction HackMIT Challenge](https://interaction.co/HackMIT)
- National Weather Service API docs: `https://www.weather.gov/documentation/services-web-api`

## 🔧 Available Tools

- `get_current_weather(location, units="metric|imperial")`: Current conditions based on NWS forecast periods
- `get_forecast(location, days=1..5, units="metric|imperial")`: Multi-day forecast (day/night periods)
- `get_weather_alerts(location)`: Official alerts/watches/warnings for the specified location

## 📝 Example Usage

```python
# Get current weather (uses NWS forecast period closest to now)
get_current_weather(location="Seattle", units="metric")

# Get 3-day forecast (day/night periods)
get_forecast(location="New York", days=3, units="imperial")

# Get weather alerts
get_weather_alerts(location="Miami")
```

Notes:
- Locations are resolved via a simple built-in mapping of major US cities. For other places, default coordinates are used. You can extend this with a geocoding service if needed.
- Current conditions are derived from the first forecast period when station observations are unavailable.
