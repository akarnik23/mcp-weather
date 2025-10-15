# Weather MCP Server

A FastMCP server that provides weather data and forecasts for Poke integration.

## 🚀 Features

- **get_current_weather**: Get current weather for any location
- **get_forecast**: Get 5-day weather forecast
- **get_weather_alerts**: Get weather alerts and warnings

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python src/server.py
```

## 🔑 API Key Setup (Optional)

For real weather data, get a free API key from [OpenWeatherMap](https://openweathermap.org/api):

```bash
export WEATHER_API_KEY=your_api_key_here
```

Without an API key, the server will return demo data.

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
4. **Set environment variable (optional):**
   - Go to your Render service dashboard
   - Click on "Environment" tab
   - Add environment variable: `WEATHER_API_KEY` = `your_openweathermap_api_key` (optional - works without it using demo data)
   - Click "Save Changes"
5. **Deploy!**

Your server will be available at `https://weather-mcp.onrender.com/mcp`

## 🎯 Poke Integration

1. Go to [poke.com/settings/connections](https://poke.com/settings/connections)
2. Add the MCP URL: `https://weather-mcp.onrender.com/mcp`
3. Give it a name like "Weather"
4. Test with: "Tell the subagent to use the Weather integration's get_current_weather tool"

## 🔧 Available Tools

- `get_current_weather(location, units="metric")`: Get current weather
- `get_forecast(location, days=5, units="metric")`: Get weather forecast
- `get_weather_alerts(location)`: Get weather alerts

## 📝 Example Usage

```python
# Get current weather
get_current_weather(location="London,UK", units="metric")

# Get 3-day forecast
get_forecast(location="New York", days=3, units="imperial")

# Get weather alerts
get_weather_alerts(location="Miami,FL")
```
