function restaurantApp() {
    return {

        restaurants: [],
        categories: [],
        priceRanges: ['$', '$$', '$$$', '$$$$'],
        selectedCategory: "",
        selectedPrice: "",
        showModal: true,
        errorMessage: "",
        loading: false,
        filteredCompanies: [],

        async init() {
            try {
                const response = await fetch('/api/restaurants');
                const data = await response.json();

                if (!data?.restaurants || !Array.isArray(data.restaurants)) {
                    throw new Error("Invalid restaurant data format");
                }


                const uniqueCats = new Set(
                    data.restaurants
                        .map((r) => r.category)
                        .filter((cat) => cat)
                );
                this.categories = Array.from(uniqueCats).sort();

            } catch (err) {
                console.error("Error fetching categories:", err);
                this.errorMessage = "Failed to load categories.";
            }
        },


        async filterByCategory() {
            if (!this.selectedCategory) {
                this.errorMessage = "Please select a category";
                return null;
            }

            try {
                const response = await fetch('/api/restaurants');
                const data = await response.json();

                const filteredRestaurants = data.restaurants.filter(restaurant =>
                    restaurant.category === this.selectedCategory
                );

                this.filteredCompanies = filteredRestaurants.map(restaurant => {
                    console.log('Processing restaurant:', restaurant.company);
                    return restaurant.company;
                });

                console.log('Category:', this.selectedCategory);
                console.log('Found restaurants:', filteredRestaurants);
                console.log('Company names to match:', this.filteredCompanies);

                return filteredRestaurants;

            } catch (err) {
                console.error("Error in category filtering:", err);
                this.errorMessage = "Failed to filter by category.";
                return null;
            }
        },

        async getYelpData() {
            if (!this.filteredCompanies.length) {
                return [];
            }

            try {
                const yelpResponse = await fetch('/data/yelp-data.json');
                const yelpData = await yelpResponse.json();

                console.log('First company to match:', this.filteredCompanies[0]);
                console.log('Sample Yelp entry:', yelpData[0]);

                const matchingYelpData = yelpData.filter(yelpEntry => {
                    const companyMatch = this.filteredCompanies.some(company =>
                        company.toLowerCase() === yelpEntry.company.toLowerCase()
                    );
                    console.log(`Comparing Yelp company "${yelpEntry.company}":`, companyMatch);
                    return companyMatch;
                });

                console.log('Found matching Yelp entries:', matchingYelpData);

                if (this.selectedPrice) {
                    return matchingYelpData.filter(item =>
                        item.yelp_data?.price === this.selectedPrice
                    );
                }

                return matchingYelpData;

            } catch (err) {
                console.error("Error fetching Yelp data:", err);
                this.errorMessage = "Failed to load Yelp data.";
                return [];
            }
        },

        async fetchFilteredRestaurants() {
            this.loading = true;
            this.errorMessage = "";
            this.restaurants = [];

            try {
                const categoryFiltered = await this.filterByCategory();
                if (!categoryFiltered) {
                    this.loading = false;
                    return;
                }

                const yelpResults = await this.getYelpData();

                this.restaurants = categoryFiltered.map(restaurant => {
                    const yelpInfo = yelpResults.find(yelp =>
                        yelp.company.toLowerCase() === restaurant.company.toLowerCase()
                    );

                    if (yelpInfo) {
                        console.log(`Matched ${restaurant.company} with Yelp data:`, yelpInfo.yelp_data);
                    }

                    return {
                        ...restaurant,
                        yelpData: yelpInfo?.yelp_data || { price: 'N/A', rating: null }
                    };
                });

                if (this.restaurants.length > 0) {
                    this.showModal = false;
                } else {
                    this.errorMessage = "No restaurants found matching your criteria.";
                }

            } catch (err) {
                console.error("Error in fetchFilteredRestaurants:", err);
                this.errorMessage = "Failed to load restaurants.";
            } finally {
                this.loading = false;
            }
        },

        submitFilters() {
            this.fetchFilteredRestaurants();
        },


        redirectToDetails(restaurant) {
            const queryParams = new URLSearchParams({
                query: restaurant.company,
                location: restaurant.address,
            });
            window.location.href = `/restaurant.html?${queryParams.toString()}`;
        },

        resetFilters() {
            this.selectedCategory = "";
            this.selectedPrice = "";
            this.restaurants = [];
            this.filteredCompanies = [];
            this.errorMessage = "";
        },

        closeModal() {
            if (this.restaurants.length > 0) {
                this.showModal = false;
            }
        },

        openModal() {
            this.showModal = true;
        }
    };
}