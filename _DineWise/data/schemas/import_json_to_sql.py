import json
import psycopg2

DB_HOST = "localhost"
DB_NAME = "your_database"
DB_USER = "your_user"
DB_PASS = "your_password"

JSON_FILE = "yelp-data.json" 

def main():
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)  # This should be a list of objects
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        for entry in data:
            restaurant_id    = entry["restaurant_id"]
            company          = entry["company"]
            yelp_business_id = entry["yelp_business_id"]
            yelp_data        = json.dumps(entry["yelp_data"])
            reviews          = json.dumps(entry["reviews"])
            sql = """
                INSERT INTO yelp_restaurants
                  (restaurant_id, company, yelp_business_id, yelp_data, reviews)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (restaurant_id) DO NOTHING;
            """
            cur.execute(sql, (restaurant_id, company, yelp_business_id, yelp_data, reviews))

    conn.close()
    print("Import complete.")

if __name__ == "__main__":
    main()
