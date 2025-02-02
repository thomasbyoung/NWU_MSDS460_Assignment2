CREATE TABLE
    restaurants (
        id INT PRIMARY KEY,
        category VARCHAR(50),
        company VARCHAR(100),
        address VARCHAR(200),
        url VARCHAR(200),
        menulink VARCHAR(200),
        facelink VARCHAR(200),
        googlink VARCHAR(200),
        wikilink VARCHAR(200),
        latitude DECIMAL(10, 8),
        longitude DECIMAL(11, 8)
    );