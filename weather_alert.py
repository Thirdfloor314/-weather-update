import pywhatkit
import requests
from datetime import datetime
import time
from geopy.geocoders import Nominatim

# Configuration
RECIPIENT_NUMBERS = ["+26879089337", "+26876897613"]  # List of Swazi Mobile numbers
LOCATION_COORDINATES = (-26.3167, 31.1333)  # Manzini coordinates
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

def get_current_weather(latitude, longitude):
    """Fetch current weather data from Open-Meteo API"""
    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True,
            "timezone": "Africa/Maputo"
        }
        response = requests.get(WEATHER_API_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Weather API error: {e}")
        return None

def get_location_name(latitude, longitude):
    """Get city/town name from coordinates"""
    try:
        geolocator = Nominatim(user_agent="swazi_weather_alerts")
        location = geolocator.reverse((latitude, longitude), exactly_one=True)
        return location.address.split(",")[0]  # Get the most specific location name
    except Exception as e:
        print(f"Geocoding error: {e}")
        return "your location"

def format_weather_message(weather_data, location_name):
    """Create formatted WhatsApp message"""
    if not weather_data:
        return "⚠️ Weather alert service is currently unavailable. Please check back later."
    
    current = weather_data.get('current_weather', {})
    temperature = current.get('temperature', 'N/A')
    weather_code = current.get('weathercode', 0)
    
    # Weather code descriptions
    weather_conditions = {
        0: "☀️ Clear sky",
        1: "🌤️ Mainly clear",
        2: "⛅ Partly cloudy",
        3: "☁️ Overcast",
        45: "🌫️ Fog",
        48: "🌫️ Freezing fog",
        51: "🌧️ Light drizzle",
        61: "🌧️ Light rain",
        80: "🌦️ Light showers",
        95: "⛈️ Thunderstorm"
    }
    
    condition = weather_conditions.get(weather_code, "🌤️ Fair weather")
    
    return (
        f"*Weather Alert for {location_name}*\n\n"
        f"🌡️ Temperature: {temperature}°C\n"
        f"☁️ Condition: {condition}\n"
        f"🕒 Last updated: {datetime.now().strftime('%a, %b %d %H:%M')}\n\n"
        f"Stay prepared! (This is an automated alert)"
    )

def send_whatsapp_alert(phone_number, message):
    """Send message via WhatsApp with error handling"""
    try:
        # Send instantly (requires WhatsApp Web to be open in browser)
        pywhatkit.sendwhatmsg_instantly(
            phone_no=phone_number,
            message=message,
            wait_time=15,
            tab_close=True
        )
        print(f"Weather alert sent to {phone_number}")
        return True
    except Exception as e:
        print(f"WhatsApp sending failed: {e}")
        return False

def main():
    print("Starting Swazi Mobile Weather Alert System...")

    # Get location and weather data
    location_name = get_location_name(*LOCATION_COORDINATES)
    weather_data = get_current_weather(*LOCATION_COORDINATES)

    # Format message
    message = format_weather_message(weather_data, location_name)
    print("Generated message:", message)

    # Send via WhatsApp to all numbers
    for number in RECIPIENT_NUMBERS:
        send_whatsapp_alert(number, message)

if __name__ == "__main__":
    # For daily automated alerts at 8AM
    while True:
        now = datetime.now()
        if now.hour == 8 and now.minute == 0:  # 8 AM
            main()
            time.sleep(60)  # Prevent duplicate sends within the same minute
        time.sleep(30)  # Check every 30 seconds
