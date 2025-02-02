CREATE TABLE
    IF NOT EXISTS yelp_restaurants (
        restaurant_id INT PRIMARY KEY,
        company TEXT NOT NULL,
        yelp_business_id TEXT NOT NULL,
        yelp_data JSONB NOT NULL,
        reviews JSONB NOT NULL
    );