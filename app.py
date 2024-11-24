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
    format_opening_hours
)

app = FastAPI()

# Load configurations from config.yaml
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

# Access configuration variables
MODEL_NAME = config['model_name']
PREDICTHQ_EVENT_LIMIT = config['limits']['predicthq_event_limit']
GOOGLE_PLACES_LIMIT = config['limits']['google_places_limit']

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
    prompt = f"Determine whether the following query is about an event or a location. Respond with only one word: 'event' or 'location'. Query: '{query}'"
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
    prompt = f"Determine whether the following query is about one of the following topics: academic, community, concerts, conferences, expos, festivals, observances, performing-arts, public-holidays, school-holidays or sports. Respond with only one word: 'academic', 'community', 'concerts', 'conferences', 'expos', 'festivals', 'observances', 'performing-arts', 'public-holidays', 'school-holidays' or 'sports'. Query: '{query}'"
    response = model.generate_content(prompt)
    return response.text

def generate_event_description(event_name: str, event_description: str, model: genai.GenerativeModel) -> str:
    """
    Formats an event description by removing the phrase 
    'Sourced from predicthq.com - ' from the input string.
    Subsequently, generates a description of the event 
    using the Gemini model

    Args:
        event_name (str): The name of the event.
        event_description (str): The original event description.
        model (genai.GenerativeModel): The generative AI model to use.

    Returns:
        str: The generated event description.
    """
    event_description = event_description.replace("Sourced from predicthq.com - ", "")
    prompt = f"Provide a 350-400 character description for the following event: {event_name}. Here is a simple description of the event that I want you to expand upon: {event_description}"
    response = model.generate_content(prompt)
    return response.text

def generate_place_description(name: str, types: List[str], model: genai.GenerativeModel) -> str:
    """
    Generate a description for a place using the Gemini model.

    Args:
        name (str): The name of the place.
        types (List[str]): A list of types/categories of the place.
        model (genai.GenerativeModel): The generative AI model to use.

    Returns:
        str: The generated description.
    """
    prompt = f"Provide a 350-400 character description for {name}, which is a {', '.join(types)}."
    response = model.generate_content(prompt)
    return response.text


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
                "Description": generate_event_description(event['title'], event.get('description', 'No description'), model),
                "Citation": event_search_URL(event['title']),
            }
            events_data.append(data)
        return events_data
    else:
        return response.status_code


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
            places_result = gmaps.places(query=q)
            places = places_result.get('results', [])

            if not places:
                return JSONResponse(content={"message": "No results found."}, status_code=404)

            # Process each place
            response_data = []
            for place in places[:GOOGLE_PLACES_LIMIT]:
                place_id = place['place_id']
                place_details = gmaps.place(place_id=place_id)['result']

                # Extract required fields and generate description using LLM
                name = place_details.get('name')
                address = place_details.get('formatted_address')
                opening_hours = format_opening_hours(place_details.get('opening_hours', {}))
                contact_number = place_details.get('formatted_phone_number')
                citation = [place_details.get('url')]
                description = generate_place_description(name, place_details.get('types', []), model)
                data = {
                    "Name": name,
                    "Address": address,
                    "Opening Hours": opening_hours,
                    "Description": description,
                    #"Top Offerings & Prices": top_offerings,
                    "Contact Number": contact_number,
                    "Citation": citation
                }
                response_data.append(data)
            return JSONResponse(content=response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
