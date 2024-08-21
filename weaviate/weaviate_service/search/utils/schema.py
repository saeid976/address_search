document_class = {
      "class": "Document",
      "description": "A class representing locations with names, addresses, and tags",
      "vectorizer": "text2vec-transformers",
      "properties": [
        {
          "name": "place_name",
          "dataType": ["text"],
          "description": "The name of the place"
        },
        {
            "name": "location",
            "dataType": ["geoCoordinates"],
            "description": "The geographical location (latitude and longitude)"
        },
        {
          "name": "address",
          "dataType": ["text"],
          "description": "The address of the place"
        },
        {
          "name": "tag",
          "dataType": ["text"],
          "description": "The category or tag associated with the place"
        }
      ]
}