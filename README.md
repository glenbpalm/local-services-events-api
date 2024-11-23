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
python3 -m venv API_env   # 
source API_env/bin/activate  # On Windows use 'venv\Scripts\activate'
```

### 3. Install Dependencies

```
pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Application using Docker

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
**Note**: Replace `<your ...>` with your actual API keys and tokens.

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
- **400**: Most likely inputted a wrong API Key.

## Example Requests & Responses

**Example URL (Events)**: `http://localhost:80/search?q=concerts`

**Response Example (Events)**:
```
[
    {
        "Title": "Stories in Art: Portable Cinema with National Gallery Singapore",
        "Start Date & Time": "23 Nov 2024 @ 0330 HRS",
        "End Date & Time": "23 Nov 2024 @ 0415 HRS",
        "Location": "1 HarbourFront Walk, Singapore 098585",
        "Description": "Sourced from predicthq.com - Join us for a storytelling session to learn about artist Chua Mia Tee’s childhood memories of watching movies through portable street carts.",
        "Citation": "https://www.google.com/search?q=Stories+in+Art:+Portable+Cinema+with+National+Gallery+Singapore"
    },
    ...
    ...
    ...
    {
        "Title": "PURE SHORES – GONGS + OCEAN DRUM SOUND MEDITATION",
        "Start Date & Time": "24 Nov 2024 @ 0400 HRS",
        "End Date & Time": "24 Nov 2024 @ 0500 HRS",
        "Location": "2 Stanley St, Singapore 068721",
        "Description": "Sourced from predicthq.com - Let the sound of the gongs and ocean drum bring you on a journey of being, lifting your spirits and soothing your heart.",
        "Citation": "https://www.google.com/search?q=PURE+SHORES+–+GONGS+++OCEAN+DRUM+SOUND+MEDITATION"
    }
]
```
---
**Example URL (Locations)**: `http://localhost:80/search?q=Local hawker centres near orchard road`

**Response Example (Locations)**:
```
[
    {
        "Name": "Newton Food Centre",
        "Address": "500 Clemenceau Ave N, Singapore 229495",
        "Opening Hours": {},
        "Description": "Newton Food Centre is a vibrant hawker centre in Singapore, a haven for local and international food lovers.  Experience authentic Singaporean cuisine at affordable prices. From sizzling satay and flavourful laksa to fragrant Hainanese chicken rice and delicious char kway teow, a diverse range of dishes awaits.  It's a bustling, atmospheric place perfect for a quick and tasty meal or a longer exploration of culinary delights.  A true Singaporean experience!\n",
        "Contact Number": null,
        "Citation": [
            "https://maps.google.com/?cid=15313617145150253769"
        ]
    },
    ...
    ...
    ...
    {
        "Name": "Whampoa Makan Place",
        "Address": "90 Whampoa Dr, Singapore 320090",
        "Opening Hours": {
            "Sun": "1100-2130",
            "Mon": "1100-2130",
            "Tue": "1100-2130",
            "Wed": "1100-2130",
            "Thu": "1100-2130",
            "Fri": "1100-2130",
            "Sat": "1100-2130"
        },
        "Description": "Whampoa Makan Place is a vibrant food haven in Singapore's Whampoa area.  This bustling establishment offers a diverse range of local delights, from hawker fare to more refined dishes. Experience authentic flavours and a lively atmosphere, perfect for a casual meal or a quick bite.  A great spot for exploring Singaporean cuisine in a friendly setting.  Expect delicious food and a bustling, energetic vibe.\n",
        "Contact Number": "9824 1696",
        "Citation": [
            "https://maps.google.com/?cid=13929068811145880670"
        ]
    }
]
```
---