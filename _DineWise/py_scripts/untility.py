import json

def add_ids_to_restaurants(file_path):
    with open(file_path, 'r') as file:
        restaurants = json.load(file)
    
    for i, restaurant in enumerate(restaurants):
        restaurant['id'] = 1000 + i
    
    with open(file_path, 'w') as file:
        json.dump(restaurants, file, indent=4)

if __name__ == "__main__":
    file_path = "./data/restaurants-v001.json"
    add_ids_to_restaurants(file_path)
    print("Successfully added IDs to restaurants")