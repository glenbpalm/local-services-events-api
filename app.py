import os
import yaml
import requests
import googlemaps
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import google.generativeai as genai
from typing import List, Dict, Any, Union

from utils import (
    format_datetime,
    format_address,
    event_search_URL,
    format_opening_hours,
    format_contact_number
)

app = FastAPI()

# Load configurations from config.yaml
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

# Access configuration variables
MODEL_NAME = config['model_name']
PREDICTHQ_EVENT_LIMIT = config['limits']['predicthq_event_limit']
GOOGLE_PLACES_LIMIT = config['limits']['google_places_limit']
INCLUDE_TOP_OFFERINGS_PRICES = config['options']['include_top_offerings_prices']

# Load environment variables
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
PREDICTHQ_API_TOKEN = os.getenv('PREDICTHQ_API_TOKEN')
GEOCODING_API_KEY = os.getenv('GEOCODING_API_KEY')

# Initialize Google Maps Client
gmaps = googlemaps.Client(key=GOOGLE_PLACES_API_KEY)

# Configure the Gemini client with the loaded credentials
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel(MODEL_NAME)

# Base URL for the TIH API
PREDICTHQ_BASE_URL = 'https://api.predicthq.com/v1/events/'

# Set up the headers with authorization
PREDICTHQ_HEADERS = {
    'Authorization': f'Bearer {PREDICTHQ_API_TOKEN}',
    'Accept': 'application/json'
}

def classify_user_query(query: str) -> str:
    """
    Classify the user's query as 'event' or 'location'.

    Args:
        query (str): The user's query string.

    Returns:
        str: The classification of the query, either 'event' or 'location'.
    """
    prompt = (
        f"Determine whether the following query is about an event or a location. "
        f"Respond with only one word: 'event' or 'location'. Query: '{query}'"
    )
    response = model.generate_content(prompt)
    classification = response.text.strip().lower()
    if 'event' in classification:
        return 'event'
    elif 'location' in classification:
        return 'location'
    else:
        # Default to 'location' if the response is unclear
        return 'location'

def classify_event(query: str) -> str:
    """
    Classify the event type from the user's query.

    Args:
        query (str): The user's query string.

    Returns:
        str: The event category (e.g., 'academic', 'concerts', etc.).
    """
    prompt = (
        "Determine whether the following query is about one of the following topics: "
        "academic, community, concerts, conferences, expos, festivals, observances, performing-arts, public-holidays, school-holidays or sports. "
        "Respond with only one word: "
        "'academic', 'community', 'concerts', 'conferences', 'expos', 'festivals', 'observances', 'performing-arts', 'public-holidays', 'school-holidays' or 'sports'. "
        f"Query: '{query}'"
    )
    response = model.generate_content(prompt)
    return response.text

def generate_event_description(event_name: str, event_description: str) -> str:
    """
    Formats an event description by removing the phrase 
    'Sourced from predicthq.com - ' from the input string.
    Subsequently, generates a description of the event 
    using the Gemini model

    Args:
        event_name (str): The name of the event.
        event_description (str): The original event description.

    Returns:
        str: The generated event description.
    """
    event_description = event_description.replace("Sourced from predicthq.com - ", "")
    prompt = (
        f"Provide a 350-400 character description for the following event: {event_name}. "
        f"Here is a simple description of the event that I want you to expand upon: {event_description}"
    )
    response = model.generate_content(prompt)
    return response.text

def generate_place_description(name: str, types: List[str]) -> str:
    """
    Generate a description for a place using the Gemini model.

    Args:
        name (str): The name of the place.
        types (List[str]): A list of types/categories of the place.

    Returns:
        str: The generated description.
    """
    prompt = f"Provide a 350-400 character description for {name}, which is a {', '.join(types)}."
    response = model.generate_content(prompt)
    return response.text

def generate_top_offerings_prices(name: str) -> Dict:
    """
    Generates a list of top offerings and their prices for a given place.
    
    Args:
    - name (str): The name of the place.
    
    Returns:
    - dict: A nested JSON object with offerings as keys and prices as values.
    """
    prompt = (
        f"Please list AT MOST the top 3 things to offer at {name} along with their prices. "
        "Format the response as '<offering>: <price>', separated by commas."
        "If price is not available, write 'NA'. "
        "Strictly do not type anything else other than those 3 pairs of offerings and prices."
    )

    # Generate response using the model with Google Search retrieval
    response = model.generate_content(
        contents=prompt,
        tools='google_search_retrieval'
    )

    # Extract the generated text
    response_text = response.text

    # Parse the response into a nested JSON object
    offerings_dict = {}
    offerings_list = response_text.split(',')
    for offering in offerings_list:
        if ':' in offering:
            key, value = offering.split(':', 1)
            offerings_dict[key.strip()] = value.strip()
        else:
            continue

    return offerings_dict


def fetch_events_from_predicthq(query: str) -> Union[List[Dict[str, Any]], int]:
    """
    Fetch events from PredictHQ API based on the query.

    Args:
        query (str): The user's query string.

    Returns:
        Union[List[Dict[str, Any]], int]: A list of event data dictionaries or a status code.
    """
    event_category = classify_event(query)
    params = {
        'category': f'{event_category}',
        'place.scope': '1880252',  # Geonames ID for Singapore
        'active.gte': datetime.now().strftime('%Y-%m-%d'),
        'active.lte': (datetime.now() + relativedelta(years=1)).strftime('%Y-%m-%d'),
        'limit': PREDICTHQ_EVENT_LIMIT,  # Number of results per page
        'sort': 'start'  # Sort by event start date
    }
    response = requests.get(PREDICTHQ_BASE_URL, headers=PREDICTHQ_HEADERS, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        events = response.json()
        events_data = []
        for event in events['results']:
            data = {
                "Title": event['title'],
                "Start Date & Time": format_datetime(event['start']),
                "End Date & Time": format_datetime(event['end']),
                "Location": format_address(event['location'], GEOCODING_API_KEY),
                "Description": generate_event_description(event['title'], event.get('description', 'No description')),
                "Citation": event_search_URL(event['title']),
            }
            events_data.append(data)
        return events_data
    else:
        return response.status_code

def fetch_locations_from_gplaces(query: str) -> Union[List[Dict[str, Any]], int]:
    """
    Fetch locations from Google Places Text Search API

    Args:
        query (str): The user's query string.

    Returns:
        Union[List[Dict[str, Any]], int]: A list of location data dictionaries or a status code.
    """
    places_result = gmaps.places(query=query)
    places = places_result.get('results', [])

    if not places:
        return JSONResponse(content={"message": "No results found."}, status_code=404)

    # Process each place
    response_data = []
    for place in places[:GOOGLE_PLACES_LIMIT]:
        place_id = place['place_id']
        place_details = gmaps.place(place_id=place_id)['result']

        # Extract required fields and generate description using Gemini Model
        name = place_details.get('name')
        address = place_details.get('formatted_address')
        opening_hours = format_opening_hours(place_details.get('opening_hours', {}))
        contact_number = format_contact_number(place_details.get('formatted_phone_number'))
        citation = [place_details.get('url')]
        description = generate_place_description(
            name, place_details.get('types', [])
        )
        data = {
            "Name": name,
            "Address": address,
            "Opening Hours": opening_hours,
            "Description": description,
            "Contact Number": contact_number,
            "Citation": citation
        }

        if INCLUDE_TOP_OFFERINGS_PRICES:
            top_offerings = generate_top_offerings_prices(name)
            data["Top Offerings & Prices"] = top_offerings

        response_data.append(data)
    return response_data


@app.get("/search")
def search(q: str) -> JSONResponse:
    """
    Search for events or places based on the user's query.

    Args:
        q (str): The query parameter from the GET request.

    Returns:
        JSONResponse: The search results in JSON format.
    """
    try:
        classification = classify_user_query(q)
        if classification == 'event':
            # Use PredictHQ Events API
            events_data = fetch_events_from_predicthq(q)
            if not events_data:
                return JSONResponse(content={"message": "No upcoming events found."}, status_code=404)
            return JSONResponse(content=events_data)
        else:
            # Use Google Places Text Search API
            response_data = fetch_locations_from_gplaces(q)
            return JSONResponse(content=response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
