import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any

def format_datetime(original_datetime_str: str) -> str:
    """
    Format a datetime string from ISO format to a readable format.

    Args:
        original_datetime_str (str): The original datetime string in ISO format.

    Returns:
        str: The formatted datetime string.
    """
    # Parse the original string into a datetime object
    dt_obj = datetime.strptime(original_datetime_str, '%Y-%m-%dT%H:%M:%SZ')

    # Add 8 hours to convert to GMT +8
    gmt8_dt_obj = dt_obj + timedelta(hours=8)

    # Format the datetime object into the desired string format
    formatted_datetime_str = gmt8_dt_obj.strftime('%d %b %Y @ %H%M HRS')

    return formatted_datetime_str

def format_address(coordinates: List[float], api_key: str) -> str:
    """
    Get the formatted address from latitude and longitude coordinates.

    Args:
        coordinates (List[float]): A list containing longitude and latitude.
        api_key (str): The API key for the Google Geocoding API.

    Returns:
        str: The formatted address or an error message.
    """
    longitude = coordinates[0]
    latitude = coordinates[1]
    url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_key}'
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            formatted_address = data['results'][0]['formatted_address']
            return formatted_address
        else:
            return 'No address found for the provided coordinates.'
    else:
        return f'Error: {response.status_code} - {response.text}'

def event_search_URL(event_title: str) -> str:
    """
    Generate a Google search URL for the event title.

    Args:
        event_title (str): The title of the event.

    Returns:
        str: The Google search URL for the event.
    """
    modified_event_title = event_title.replace(' ', '+')
    google_search = f"https://www.google.com/search?q={modified_event_title}"
    return google_search

def format_opening_hours(opening_hours: Dict[str, Any]) -> Dict[str, str]:
    """
    Format the opening hours from the place details.

    Args:
        opening_hours (Dict[str, Any]): The opening hours data from place details.

    Returns:
        Dict[str, str]: A dictionary mapping days to opening hours.
    """
    try:
        periods = opening_hours.get('periods', [])
        week_hours = {}
        days_map = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        for day in range(7):
            day_name = days_map[day]
            for period in periods:
                if period['open']['day'] == day:
                    open_time = period['open']['time']
                    close_time = period['close']['time']
                    week_hours[day_name] = f"{open_time}-{close_time}"
        return week_hours
    except:
        return {}

def format_contact_number(number: str) -> str:
    """
    Formats a Singaporean contact number to the format +65-XXXX-XXXX.
    Handles NoneType inputs gracefully.

    Args:
        number (str): The input contact number in the format 'XXXX XXXX', or None.

    Returns:
        str: The formatted contact number in the format '+65-XXXX-XXXX',
             or 'None' if the input is None or invalid.
    """
    if number is None:
        return "None"
    
    # Ensure the input is a string
    if not isinstance(number, str):
        return "None"

    # Remove any whitespace from the input
    cleaned_number = number.replace(" ", "")
    
    # Check if the cleaned number has exactly 8 digits and is numeric
    if len(cleaned_number) != 8 or not cleaned_number.isdigit():
        return "None"

    # Format the number with the Singapore country code
    formatted_number = f"+65-{cleaned_number[:4]}-{cleaned_number[4:]}"
    return formatted_number