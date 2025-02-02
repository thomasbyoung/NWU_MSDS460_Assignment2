# DineWise

DineWise is a web application that helps users discover and explore restaurants in the Marlborough, MA area. It provides detailed restaurant information, Yelp integration for reviews and ratings, and a category-based filtering system.

## Features

- Browse local restaurants by category
- View restaurant details including:
  - Menu links
  - Contact information
  - Location details
- Yelp integration providing:
  - Ratings and reviews
  - Price ranges
  - Additional business details

## Setup

### Prerequisites

- Go 1.19 or higher
- PostgreSQL
- Python 3.8 or higher (for data scripts)

### Installation

1. Clone the repository:

2. Install Go dependencies:

```bash
go mod tidy
```

3. Create a `.env` file in the project root:

```env
YELP_API_KEY=your_yelp_api_key_here
DB_CONNECTION_STRING=postgres://username:password@localhost:5432/dinewise
```

4. Set up the database:

```bash
psql -U your_username -d postgres
CREATE DATABASE dinewise;
```

5. Run the schema migrations (located in ./data/schemas)

### Configuration

#### Yelp API Setup

1. Visit [Yelp Fusion](https://fusion.yelp.com/)
2. Create an account and generate an API key
3. Add the key to your `.env` file

#### Database Schema

Database schemas are located in `./data/schemas/`. These define the structure for:

- Restaurants
- Categories
- Reviews
- User preferences

## Running the Application

1. Start the server:

```bash
go run main.go
```

2. Access the application:

- Open `http://localhost:8081` in your browser
- Main restaurant listing is available at `/`
- Restaurant details are at `/restaurant.html?query=restaurant_name`

## Data Structure

### Restaurant Data

Restaurant information is stored in `./data/restaurants-v001.json` ans `./data/yelp-data.json` with the following structure:

```json
{
  "id": "1000",
  "category": "American",
  "company": "Restaurant Name",
  "address": "Full Address",
  "url": "Website URL",
  "menulink": "Menu URL",
  "latitude": "",
  "longitude": ""
}
```

```json
    {
        "restaurant_id": 1000,
        "company": "110 Grill",
        "yelp_business_id": "XdtVjkDIqS67f504WDjGOg",
        "yelp_data": {
            "id": "XdtVjkDIqS67f504WDjGOg",
            "name": "110 Grill",
            "rating": 3.9,
            "review_count": 320,
            "price": "$$",
            "phone": "+15082512027",
            "url": "https://www.yelp.com/biz/110-grill-marlborough-7?adjust_creative=fxUSo76vVrMe2lSZboD79w&utm_campaign=yelp_api_v3&utm_medium=api_v3_graphql&utm_source=fxUSo76vVrMe2lSZboD79w",
            "photos": [
                "https://s3-media3.fl.yelpcdn.com/bphoto/LFT7-b2PJE6SJViKQ2n5yg/o.jpg"
            ]
        }
```

### Yelp Data

Individual restaurant page details are fetched from Yelp's GraphQL API when viewing restaurant details.

## Scripts

### Data Management

- `fetch_yelp_data.py`: Batch fetch Yelp data for all restaurants
- Additional data processing scripts in `./scripts/`

## Future Enhancements

### Planned Features

1. **Location-Based Sorting**

   - Sort restaurants by proximity to user's location
   - Filter results by distance radius

2. **Review Analysis**

   - Encode and analyze review content
   - Generate sentiment analysis
   - Provide keyword-based search

3. **Chatbot Interface**

   - Natural language restaurant search
   - Preference-based recommendations
   - Dietary restriction filtering

4. **Enhanced Data Integration**
   - Real-time menu updates
   - Price range tracking
   - Special offers integration

### Technical Roadmap

1. Implement PostgreSQL integration
2. Add geospatial queries for location-based features
3. Implement review encoding system
4. Develop chatbot interface

## API Documentation

### Endpoints

#### GET /api/restaurants

Returns all restaurants in the database

#### GET /api/yelp-graphql-search

Requires Yelp API key. Returns detailed information about a specific restaurant.

Parameters:

- `term`: Restaurant name
- `location`: Restaurant address

#### GET /api/yelp-graphql-reviews

Requires Yelp API key. Returns reviews for a specific restaurant.

Parameters:

- `businessId`: Yelp business ID

## License

This project is licensed under the MIT License - see the LICENSE file for details
