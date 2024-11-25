# Local Services and Events API

This is a cloud-hosted API that allows users to search for local events or places based on their queries. It integrates with multiple external APIs to provide comprehensive and up-to-date information.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Installation](#installation)
- [Running the Application Using Docker](#running-the-application-using-docker)
- [API Endpoints](#api-endpoints)
- [Example Requests & Responses](#example-requests--responses)

## Features
- **Intelligent Query Classification**: Utilises Gemini model to classify user queries as either events or locations.
- **Event Search**: Fetches upcoming events in Singapore using the PredictHQ API based on user queries.
- **Location Search**: Retrieves place details from the Google Places API based on user queries.
- **Dynamic Descriptions**: Generates detailed descriptions for places using Gemini model.
- **Formatted Output**: Provides well-structured JSON responses with essential information like addresses, opening hours and contact details.

## Prerequisites
- Python 3.9 or higher
- Docker
- API Keys and Tokens for:
  - Google Places API
  - Google Geocoding API
  - PredictHQ API
  - Gemini Model

## Environment Variables
The application requires the following environment variables to be set:
- `GOOGLE_PLACES_API_KEY`: Your Google Places API Key.
- `GEMINI_API_KEY`: Your Gemini API Key.
- `PREDICTHQ_API_TOKEN`: Your PredictHQ API Token.
- `GEOCODING_API_KEY`: Your Google Geocoding API Key.

## Installation

### 1. Clone the Repository

```
git clone https://github.com/glenbpalm/local-services-events-api.git
cd local-services-events-api
```

### 2. Create a Virtual Environment

```
python3 -m venv API_env
source API_env/bin/activate  # On Windows use 'venv\Scripts\activate'
```

### 3. Install Dependencies

```
pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Application using Docker

### Setting Configurations
Set the desired configurations in the `config.yaml` file:
```
model_name: "gemini-1.5-flash"

limits:
  predicthq_event_limit: 5
  google_places_limit: 5

options:
  include_top_offerings_prices: False
```
- **model_name**: Define which Gemini Model is to be used. Default model is Gemini 1.5 Flash.
- **predicthq_event_limit**: Set the number of events to fetch from PredictHQ.
- **google_places_limit**: Set the number of places to fetch from Google Places API
- **include_top_offerings_prices**: State whether or not to generate Top Offerings & Prices for each location. Can either be True or False. Default value is `False` due to the fact that setting it to `True` will slow down inference time. This is because it uses the the Gemini Models' Google Search Retrieval Tool (inaccurate at times as well).

### Building the Docker Image
Build the Docker Image with the tag `local-services-api`:
```
docker build -t local-services-api .
```

### Running the Docker Container
Run the Docker container while passing the required environment variables:
```
docker run --name gcloud-gemini-container -d \
  -p 80:80 \
  -e GOOGLE_PLACES_API_KEY=<your Google Places API Key> \
  -e GEMINI_API_KEY=<your Gemini API Key> \
  -e PREDICTHQ_API_TOKEN=<your PredictHQ API token> \
  -e GEOCODING_API_KEY=<your Google Geocoding API Key> \
  local-services-api
```
**Note**: Replace `<your ...>` with your actual API keys and tokens ( E.g. GOOGLE_PLACES_API_KEY=CYbgk.......ogjP )

## API Endpoints

### GET `/search`
Searches for events or places based on the user's query. The endpoint determines whether the query is about an event or a location.

### Requesting using Postman
You can test the API endpoint using Postman by following these steps:
1. Launch the Postman application
2. Create a New Request
   - Click on "New" and select "HTTP Request".
3. Set the Request Method and URL
   - Change the request method to GET.
   - Enter the URL: `http://localhost:80/search`
4. Add Query Parameters
   - Click on the "Params" tab below the URL field.
   - Add a new key-value pair:
      - Key: `q`
      - Value: Your search query (e.g., `concerts`)
5. Send the Request
   - Click on the "Send" button.
6. View the Response
   - The API's JSON response will appear in the response pane below.
   - You can switch between Pretty, Raw, and Preview to view the response in different formats.

### Notes
- Ensure that the API is running and accessible at `http://localhost:80`.
- If you're running the API inside a Docker container, make sure the container's ports are correctly mapped to your host machine.
- If you're testing on a remote server, replace `localhost` with the server's IP address or domain name.

### Troubleshooting
- **No Response**: Check if the API is running and if the port is correct.
- **Error Responses**: Refer to the [Error Responses](#error-responses) section for more information.

### Error Responses
- **404**: No results found for the given query.
- **500**: An error occurred while processing the request.
- **400**: The server cannot process the request due to something that is perceived to be a client error (e.g. malformed request syntax, invalid request parameters, wrong API Key)
- **429**: Resource exhausted, exceeded API rate limits. This error occurs when using the free-of-charge Gemini API, and setting `include_top_offerings_prices` to `True` in the `config.yaml` file. This error should be resolved when using the paid Gemini API plan.

## Example Requests & Responses

**Example URL (Events)**: `http://localhost:80/search?q=give me some concerts that are coming up`

**Response Example (Events)**:
```
[
    {
        "Title": "OFFERING OF GONGS + SINGING BOWLS SOUND",
        "Start Date & Time": "25 Nov 2024 @ 1100 HRS",
        "End Date & Time": "25 Nov 2024 @ 1200 HRS",
        "Location": "2 Stanley St, Singapore 068721",
        "Description": "Immerse yourself in a sacred sonic cleansing.  Our Offering of Gongs & Singing Bowls purifies the temple's energy, creating a receptive space for inner peace.  Deep resonant vibrations wash away negativity, leaving you cleansed and open to the present moment.  Experience the transformative power of sound as it harmonizes your body and spirit, fostering a profound connection to yourself and the divine. This ancient practice leaves you feeling renewed and centered.\n",
        "Citation": "https://www.google.com/search?q=OFFERING+OF+GONGS+++SINGING+BOWLS+SOUND"
    },
    ...
    ...
    ...
    {
        "Title": "HEAL FROM WITHIN: AFFIRMATIONS + TIBETAN SINGING BOWLS + OCEAN DRUM",
        "Start Date & Time": "26 Nov 2024 @ 2000 HRS",
        "End Date & Time": "26 Nov 2024 @ 2100 HRS",
        "Location": "2 Stanley St, Singapore 068721",
        "Description": "Unleash your inner healer at HEAL FROM WITHIN!  Experience the transformative power of positive affirmations, resonating Tibetan singing bowls, and the mesmerizing ocean drum. This immersive practice gently guides you to reconnect with your body's innate wisdom, releasing stress and promoting deep relaxation.  Feel your energy revitalized as ancient sounds and empowering words unlock your self-healing potential, leaving you feeling calm, centered, and profoundly renewed.  Journey to a place of deep peace and well-being.\n",
        "Citation": "https://www.google.com/search?q=HEAL+FROM+WITHIN:+AFFIRMATIONS+++TIBETAN+SINGING+BOWLS+++OCEAN+DRUM"
    }
]
```
---
**Example URL (Locations)**: `http://localhost:80/search?q=Local hawker centres near orchard road`

**Response Example (Locations with Top Offerings ON)**:
```
[
    {
        "Name": "Newton Food Centre",
        "Address": "500 Clemenceau Ave N, Singapore 229495",
        "Opening Hours": {},
        "Description": "Newton Food Centre is a vibrant hawker centre in Singapore, a haven for local and international food lovers.  Experience authentic Singaporean cuisine at affordable prices. From sizzling satay and flavourful laksa to fragrant Hainanese chicken rice and delicious char kway teow, a diverse range of dishes awaits.  It's a bustling, atmospheric place perfect for a quick and tasty meal or a longer exploration of culinary delights.  A true Singaporean experience!\n",
        "Contact Number": "None",
        "Citation": [
            "https://maps.google.com/?cid=15313617145150253769"
        ],
        "Top Offerings & Prices": {
            "Satay": "$0.80/stick (min 10)",
            "BBQ chicken wings": "$1.50/pc (min 3)",
            "Chilli Crab": "NA"
        }
    },
    ...
    ...
    ...
    {
        "Name": "Chinatown Complex Market & Food Centre",
        "Address": "46 Smith St, Singapore 058956",
        "Opening Hours": {
            "Sun": "0800-2100",
            "Mon": "0800-2100",
            "Tue": "0800-2100",
            "Wed": "0800-2100",
            "Thu": "0800-2100",
            "Fri": "0800-2100",
            "Sat": "0800-2100"
        },
        "Description": "Chinatown Complex Market & Food Centre is a vibrant hawker centre in Singapore's Chinatown.  This bustling establishment offers a huge variety of affordable and delicious local cuisine, from traditional noodles and rice dishes to unique snacks.  Expect a lively atmosphere, packed with locals and tourists alike, all enjoying the authentic flavours and cultural immersion.  A must-visit for food lovers exploring Singapore's culinary scene.\n",
        "Contact Number": "None",
        "Citation": [
            "https://maps.google.com/?cid=13315514385399549060"
        ],
        "Top Offerings & Prices": {
            "Laksa": "$2",
            "Hong Kong Soya Sauce Chicken": "NA",
            "Claypot Rice": "$8"
        }
    }
]
```
---