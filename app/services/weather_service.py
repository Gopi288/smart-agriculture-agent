"""Weather service integration for Smart Agriculture Agent.

Fetches live agrometeorological data from OpenWeatherMap API when an API key
is present, with resilient offline fallback, explicit source attribution,
and timeout handling. Never fabricates live weather data.
"""

from datetime import datetime
from typing import Any, Dict, Optional
import requests


class WeatherService:
    """Service to fetch and validate weather data for agricultural decision support."""

    def __init__(self, api_key: str = "", timeout: int = 5, base_url: str = "https://api.openweathermap.org/data/2.5/weather"):
        self.api_key = api_key.strip() if api_key else ""
        self.timeout = timeout
        self.base_url = base_url

    @property
    def is_configured(self) -> bool:
        """Check whether a non-empty API key is configured."""
        return bool(self.api_key)

    def get_weather(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Fetch current weather data for a specified location.

        Args:
            location: City name or geographic query (e.g., 'Fresno', 'Bengaluru').

        Returns:
            Dictionary containing weather metrics, data source, and status.
        """
        now_iso = datetime.now().isoformat()

        # If not configured or location is missing, return transparent offline status
        if not self.is_configured:
            return {
                "is_available": False,
                "source": "Unavailable (No OpenWeather API key configured)",
                "location": location or "Not Specified",
                "temperature_c": None,
                "humidity_pct": None,
                "condition": None,
                "timestamp": now_iso,
                "note": "OpenWeather API key is not configured. Irrigation advisor operates using soil moisture and manual rainfall readings.",
            }

        if not location or not str(location).strip():
            return {
                "is_available": False,
                "source": "Unavailable (Location not provided)",
                "location": "Not Specified",
                "temperature_c": None,
                "humidity_pct": None,
                "condition": None,
                "timestamp": now_iso,
                "note": "Provide a valid location name to retrieve live weather observations.",
            }

        try:
            params = {
                "q": str(location).strip(),
                "appid": self.api_key,
                "units": "metric",  # Celsius, mm
            }
            resp = requests.get(self.base_url, params=params, timeout=self.timeout)

            if resp.status_code == 200:
                data = resp.json()
                main = data.get("main", {})
                weather_list = data.get("weather", [{}])
                condition = weather_list[0].get("description", "Clear").title() if weather_list else "Clear"

                return {
                    "is_available": True,
                    "source": "OpenWeatherMap Live API",
                    "location": data.get("name", location),
                    "temperature_c": round(float(main.get("temp", 0.0)), 1),
                    "humidity_pct": round(float(main.get("humidity", 0.0)), 1),
                    "condition": condition,
                    "timestamp": now_iso,
                    "note": "Live meteorological telemetry retrieved successfully.",
                }
            elif resp.status_code == 404:
                return {
                    "is_available": False,
                    "source": "OpenWeatherMap API",
                    "location": location,
                    "temperature_c": None,
                    "humidity_pct": None,
                    "condition": None,
                    "timestamp": now_iso,
                    "note": f"Location '{location}' not found by weather service.",
                }
            elif resp.status_code == 401:
                return {
                    "is_available": False,
                    "source": "OpenWeatherMap API",
                    "location": location,
                    "temperature_c": None,
                    "humidity_pct": None,
                    "condition": None,
                    "timestamp": now_iso,
                    "note": "OpenWeatherMap API key is invalid or unauthorized.",
                }
            else:
                return {
                    "is_available": False,
                    "source": "OpenWeatherMap API",
                    "location": location,
                    "temperature_c": None,
                    "humidity_pct": None,
                    "condition": None,
                    "timestamp": now_iso,
                    "note": f"Weather API returned status code {resp.status_code}.",
                }

        except requests.exceptions.Timeout:
            return {
                "is_available": False,
                "source": "OpenWeatherMap API (Timed out)",
                "location": location,
                "temperature_c": None,
                "humidity_pct": None,
                "condition": None,
                "timestamp": now_iso,
                "note": f"Weather API request timed out after {self.timeout}s. Fallback rules active.",
            }
        except requests.exceptions.RequestException as exc:
            return {
                "is_available": False,
                "source": "OpenWeatherMap API (Connection Error)",
                "location": location,
                "temperature_c": None,
                "humidity_pct": None,
                "condition": None,
                "timestamp": now_iso,
                "note": f"Network error communicating with weather provider: {str(exc)}",
            }
