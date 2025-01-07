from fastapi import FastAPI
from pydantic import BaseModel
import requests

# Define the FastAPI app
app = FastAPI()

class GeoQuery(BaseModel):
    location: str
    analysis_type: str

class GeoGPT:
    """
    GeoGPT is a geographic and climatic analysis agent that provides insights into 
    current geographic and climatic situations based on input location and analysis type.
    """
    def __init__(self):
        self.weather_api_url = "https://api.open-meteo.com/v1/forecast"
        self.map_api_url = "https://nominatim.openstreetmap.org/search"

    def fetch_weather_data(self, location):
        """Fetches weather data for the given location using Open-Meteo API."""
        try:
            params = {
                'latitude': location['lat'],
                'longitude': location['lon'],
                'current_weather': True
            }
            response = requests.get(self.weather_api_url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def fetch_location_data(self, location_name):
        """Fetches geographic coordinates for a location name using OpenStreetMap API."""
        try:
            params = {
                'q': location_name,
                'format': 'json',
                'limit': 1
            }
            response = requests.get(self.map_api_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data:
                return {'lat': float(data[0]['lat']), 'lon': float(data[0]['lon'])}
            else:
                return {"error": "Location not found"}
        except Exception as e:
            return {"error": str(e)}

    def analyze(self, location_name, analysis_type):
        """Analyzes the geographic or climatic situation based on the analysis type."""
        location_data = self.fetch_location_data(location_name)

        if "error" in location_data:
            return location_data

        if analysis_type == "weather":
            return self.fetch_weather_data(location_data)

        elif analysis_type == "geography":
            return {
                "location": location_name,
                "coordinates": location_data
            }

        else:
            return {"error": "Unsupported analysis type. Use 'weather' or 'geography'."}

# Instantiate the GeoGPT agent
geo_gpt_agent = GeoGPT()

@app.post("/analyze")
async def analyze(query: GeoQuery):
    """API endpoint to interact with GeoGPT for geographic/climatic analysis."""
    return geo_gpt_agent.analyze(query.location, query.analysis_type)

# To run the app, use a command like:
# uvicorn geo_gpt_agent:app --reload
