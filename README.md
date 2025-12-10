# HTTP Metadata Inventory & FastAPI Endpoint

A FastAPI-based service that collects and stores HTTP metadata (headers, cookies, page source) for URLs using MongoDB.

## Features

- **POST /collect**: Submit a URL to collect its metadata
- **GET /metadata**: Retrieve stored metadata or trigger collection if not available
- Asynchronous metadata collection using background tasks
- MongoDB storage with automatic indexing
- Docker Compose setup for easy deployment
- Comprehensive test suite using pytest

## Technical Stack

- **Framework**: FastAPI
- **Database**: MongoDB
- **Infrastructure**: Docker Compose
- **HTTP Client**: httpx
- **Testing**: pytest

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository or navigate to the project directory:
```bash
cd http-metadata-inventory
```

2. Start the services:
```bash
docker-compose up --build
```

3. The API will be available at `http://localhost:8000`

4. Access the interactive API documentation at `http://localhost:8000/docs`

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure MongoDB is running locally on port 27017

3. Run the application:
```bash
uvicorn main:app --reload
```

## API Endpoints

### POST /collect

Collect metadata for a URL.

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "url": "https://example.com",
  "status": "processing",
  "message": "Metadata collection started"
}
```

### GET /metadata

Retrieve metadata for a URL.

**Request:**
```
GET /metadata?url=https://example.com
```

**Response (if exists):**
```json
{
  "url": "https://example.com",
  "headers": {...},
  "cookies": {...},
  "page_source": "...",
  "collected_at": "2024-01-01T12:00:00",
  "status": "exists",
  "message": "Metadata retrieved successfully"
}
```

**Response (if not exists):**
```json
{
  "url": "https://example.com",
  "status": "not_found",
  "message": "Record doesn't exist & request has been logged to collect the metadata, please check later"
}
```

## Running Tests

### Using Docker

```bash
docker-compose run api pytest test_main.py -v
```

### Local

```bash
pytest test_main.py -v
```

## Project Structure

```
http-metadata-inventory/
├── main.py                 # FastAPI application
├── test_main.py           # Test suite
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image configuration
├── docker-compose.yml    # Docker Compose setup
└── README.md            # This file
```

## How It Works

1. **POST /collect**: When you submit a URL, the API immediately returns a response and starts collecting metadata in the background.

2. **GET /metadata**: 
   - If the URL exists in the database, it returns the stored metadata
   - If the URL doesn't exist, it triggers background collection and returns a message to check later

3. **Background Collection**: The service uses FastAPI's BackgroundTasks to asynchronously fetch:
   - HTTP headers
   - Cookies
   - Page source (HTML content)
   - Response status code

4. **Storage**: All metadata is stored in MongoDB with the URL as the unique identifier.

## Environment Variables

- `MONGODB_URL`: MongoDB connection string (default: `mongodb://mongodb:27017`)

## Stopping the Services

```bash
docker-compose down
```

To remove volumes as well:
```bash
docker-compose down -v
```

## License

MIT

## Author

Created as part of a technical assignment.
