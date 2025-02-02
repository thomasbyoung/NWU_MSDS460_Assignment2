import json
import requests
import time
from urllib.parse import quote

class YelpDataFetcher:
    def __init__(self, base_url="http://localhost:8081"):
        self.base_url = base_url
        self.restaurants_file = "./data/restaurants-v001.json"
        self.yelp_data_file = "./data/yelp-data.json"
        self.failed_searches_file = "./data/failed_searches.json"
        self.failed_searches = []

    def load_restaurants(self):
        try:
            with open(self.restaurants_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Error: Could not find file: {self.restaurants_file}")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in file: {self.restaurants_file}")
            return []

    def save_yelp_data(self, yelp_data):
        with open(self.yelp_data_file, 'w') as file:
            json.dump(yelp_data, file, indent=4)

    def save_failed_searches(self):
        with open(self.failed_searches_file, 'w') as file:
            json.dump(self.failed_searches, file, indent=4)

    def fetch_yelp_data(self, restaurant):
    \
        params = {
            'term': restaurant['company'],
            'location': restaurant['address']
        }
        
        search_url = f"{self.base_url}/api/yelp-graphql-search"
        
        try:
            print(f"\nSearching for: {restaurant['company']}")
            print(f"Using location: {restaurant['address']}")
            
            response = requests.get(search_url, params=params)
            if not response.ok:
                print(f"Search request failed: {response.status_code}")
                print(f"Response: {response.text}")
                self.failed_searches.append({
                    'restaurant': restaurant,
                    'error': f'HTTP {response.status_code}',
                    'response': response.text
                })
                return None

            business_data = response.json()
            
            if 'errors' in business_data:
                print(f"Yelp API Error: {json.dumps(business_data['errors'], indent=2)}")
                self.failed_searches.append({
                    'restaurant': restaurant,
                    'error': 'Yelp API Error',
                    'details': business_data['errors']
                })
                return None

            business = None
            if business_data.get('data', {}).get('search', {}).get('business'):
                business = business_data['data']['search']['business'][0]
            else:
                print(f"No business data found for: {restaurant['company']}")
                self.failed_searches.append({
                    'restaurant': restaurant,
                    'error': 'No Business Found'
                })
                return None

            reviews = []
            if business and business.get('id'):
                reviews_url = f"{self.base_url}/api/yelp-graphql-reviews"
                reviews_params = {'businessId': business['id']}
                
                reviews_response = requests.get(reviews_url, params=reviews_params)
                if reviews_response.ok:
                    reviews_data = reviews_response.json()
                    if 'data' in reviews_data and 'business' in reviews_data['data']:
                        reviews = reviews_data['data']['business'].get('reviews', [])
                else:
                    print(f"Failed to fetch reviews: {reviews_response.text}")

            yelp_entry = {
                'restaurant_id': restaurant.get('id'),
                'company': restaurant['company'],
                'yelp_business_id': business.get('id'),
                'yelp_data': business,
                'reviews': reviews
            }

            return yelp_entry

        except requests.RequestException as e:
            print(f"Network error for {restaurant['company']}: {str(e)}")
            self.failed_searches.append({
                'restaurant': restaurant,
                'error': 'Network Error',
                'details': str(e)
            })
            return None
        except Exception as e:
            print(f"Unexpected error for {restaurant['company']}: {str(e)}")
            self.failed_searches.append({
                'restaurant': restaurant,
                'error': 'Unexpected Error',
                'details': str(e)
            })
            return None

    def process_all_restaurants(self):
        restaurants = self.load_restaurants()
        if not restaurants:
            print("No restaurants to process")
            return

        yelp_data = []
        total = len(restaurants)
        
        for i, restaurant in enumerate(restaurants, 1):
            print(f"\nProcessing {i}/{total}: {restaurant['company']}")
            
            yelp_entry = self.fetch_yelp_data(restaurant)
            if yelp_entry:
                yelp_data.append(yelp_entry)
                print(f"Successfully processed {restaurant['company']}")
            else:
                print(f"Failed to process {restaurant['company']}")
            
            time.sleep(1)

        if yelp_data:
            self.save_yelp_data(yelp_data)
            print(f"\nProcessed {len(yelp_data)} restaurants successfully")
            print(f"Data saved to: {self.yelp_data_file}")
        else:
            print("\nNo data was collected successfully")
        if self.failed_searches:
            self.save_failed_searches()
            print(f"\nFailed searches: {len(self.failed_searches)}")
            print(f"Failed searches saved to: {self.failed_searches_file}")

if __name__ == "__main__":
    fetcher = YelpDataFetcher()
    fetcher.process_all_restaurants()