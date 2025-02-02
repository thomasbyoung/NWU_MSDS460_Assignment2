package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/joho/godotenv"
)

type Restaurant struct {
	Category  string `json:"category"`
	Company   string `json:"company"`
	Address   string `json:"address"`
	URL       string `json:"url"`
	MenuLink  string `json:"menulink"`
	FaceLink  string `json:"facelink"`
	GoogLink  string `json:"googlink"`
	WikiLink  string `json:"wikilink"`
	Latitude  string `json:"latitude"`
	Longitude string `json:"longitude"`
}

func loadRestaurants() ([]Restaurant, error) {
	fileBytes, err := os.ReadFile("data/restaurants-v001.json")
	if err != nil {
		return nil, err
	}

	var restaurants []Restaurant
	if err := json.Unmarshal(fileBytes, &restaurants); err != nil {
		return nil, err
	}

	return restaurants, nil
}

func getRestaurants(w http.ResponseWriter, r *http.Request) {
	restaurants, err := loadRestaurants()
	if err != nil {
		http.Error(w, "Failed to load data", http.StatusInternalServerError)
		return
	}

	response := struct {
		Restaurants []Restaurant `json:"restaurants"`
	}{
		Restaurants: restaurants,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func postYelpGraphQLQuery(query string) (io.ReadCloser, error) {
	apiKey := os.Getenv("YELP_API_KEY")
	if apiKey == "" {
		log.Println("Error: YELP_API_KEY not found in environment")
		return nil, fmt.Errorf("no Yelp API key set in environment")
	}
	log.Printf("Sending GraphQL query: %s\n", query)
	requestBody := map[string]interface{}{
		"query":     query,
		"variables": map[string]interface{}{},
	}

	jsonBody, err := json.Marshal(requestBody)
	if err != nil {
		log.Printf("Error marshaling request body: %v\n", err)
		return nil, fmt.Errorf("failed to marshal GraphQL query: %w", err)
	}
	log.Printf("Sending request body: %s\n", string(jsonBody))
	req, err := http.NewRequest("POST", "https://api.yelp.com/v3/graphql", bytes.NewBuffer(jsonBody))
	if err != nil {
		log.Printf("Error creating request: %v\n", err)
		return nil, fmt.Errorf("failed to create GraphQL request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", apiKey))

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		log.Printf("Error making request: %v\n", err)
		return nil, fmt.Errorf("failed to contact Yelp GraphQL: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		resp.Body.Close()
		log.Printf("Yelp API error response: %s\n", string(body))
		return nil, fmt.Errorf("Yelp GraphQL error %d: %s", resp.StatusCode, string(body))
	}

	return resp.Body, nil
}

func yelpGraphQLSearchHandler(w http.ResponseWriter, r *http.Request) {
	term := r.URL.Query().Get("term")
	if term == "" {
		http.Error(w, "Missing 'term' query parameter", http.StatusBadRequest)
		return
	}
	location := r.URL.Query().Get("location")
	if location == "" {
		location = "Marlborough, MA"
	}

	graphqlQuery := fmt.Sprintf(`query {
        search(term: "%s", location: "%s", limit: 1) {
            total
            business {
                id
                name
                rating
                review_count
                price
                phone
                url
                photos
            }
        }
    }`, escapeString(term), escapeString(location))

	body, err := postYelpGraphQLQuery(graphqlQuery)
	if err != nil {
		log.Printf("Search handler error: %v\n", err)
		http.Error(w, fmt.Sprintf("Failed to fetch from Yelp: %v", err), http.StatusInternalServerError)
		return
	}
	defer body.Close()
	responseData, err := io.ReadAll(body)
	if err != nil {
		log.Printf("Error reading response: %v\n", err)
		http.Error(w, "Error reading response", http.StatusInternalServerError)
		return
	}

	log.Printf("Yelp response: %s\n", string(responseData))

	w.Header().Set("Content-Type", "application/json")
	w.Write(responseData)
}

func yelpGraphQLReviewsHandler(w http.ResponseWriter, r *http.Request) {
	businessID := r.URL.Query().Get("businessId")
	if businessID == "" {
		http.Error(w, "Missing 'businessId' query param", http.StatusBadRequest)
		return
	}

	graphqlQuery := fmt.Sprintf(`query {
        business(id: "%s") {
            name
            reviews(limit: 3) {
                id
                rating
                text
                time_created
                user {
                    name
                }
            }
        }
    }`, escapeString(businessID))

	body, err := postYelpGraphQLQuery(graphqlQuery)
	if err != nil {
		log.Printf("Reviews handler error: %v\n", err)
		http.Error(w, fmt.Sprintf("Failed to fetch reviews from Yelp: %v", err), http.StatusInternalServerError)
		return
	}
	defer body.Close()

	w.Header().Set("Content-Type", "application/json")
	io.Copy(w, body)
}

func escapeString(s string) string {
	s = strings.ReplaceAll(s, "\\", "\\\\")
	s = strings.ReplaceAll(s, "\"", "\\\"")
	s = strings.ReplaceAll(s, "\n", "\\n")
	s = strings.ReplaceAll(s, "\r", "\\r")
	s = strings.ReplaceAll(s, "\t", "\\t")
	return s
}

func main() {
	err := godotenv.Load(".env")
	if err != nil {
		log.Println("No .env file found or error loading it:", err)
	}
	fs := http.FileServer(http.Dir("static"))
	http.Handle("/", fs)
	http.HandleFunc("/api/restaurants", getRestaurants)
	http.HandleFunc("/api/yelp-graphql-search", yelpGraphQLSearchHandler)
	http.HandleFunc("/api/yelp-graphql-reviews", yelpGraphQLReviewsHandler)
	http.Handle("/data/", http.StripPrefix("/data/", http.FileServer(http.Dir("data"))))

	fmt.Println("Server running on http://localhost:8081/")
	log.Fatal(http.ListenAndServe(":8081", nil))
}
