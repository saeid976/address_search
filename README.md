# Search Microservices
This repository contains two separate microservices for data indexing and search capabilities. Each microservice utilizes a different technology stack to provide search functionalities: Weaviate and Elasticsearch. Below you'll find a detailed explanation of each directory and its corresponding technology.


## Weaviate Microservice

The `weaviate` directory contains a microservice that leverages the Weaviate vector database for advanced search functionalities.

### Overview

Weaviate is a vector database that uses vector embeddings to enable semantic search capabilities. It indexes and searches data using the [HNSW](https://weaviate.io/developers/academy/py/vector_index/hnsw) (Hierarchical Navigable Small World) algorithm, which allows for efficient nearest-neighbor search in high-dimensional spaces.

### Features

- **Vector Search**: Utilizes vector embeddings to perform semantic searches.
- **HNSW Algorithm**: Provides efficient and scalable nearest-neighbor search.
- **Integration**: Can be integrated with machine learning models to enhance search capabilities.

### Setup

1. **Pull Docker Image**: Pull the Weaviate Docker image from the Docker registry.
2. **Configure Docker Compose**: Set the Weaviate image name in the `docker-compose.yml` file located in the `weaviate` directory.
3. **Build Docker Image**: Run the following command to build the Docker image:
   ```bash
   docker compose up --build
4. **Access FastAPI UI**: Once the service is running, you can access the FastAPI UI at localhost:8000/docs.
## Elasticsearch Microservice

The `elasticsearch` directory contains a microservice that utilizes Elasticsearch for search and data indexing.

### Overview

Elasticsearch is a powerful search engine based on the Lucene library. It uses an inverted index data structure, which allows for fast and efficient full-text searches and analytics.

### Features

- **Full-Text Search**: Provides fast and accurate full-text search capabilities.
- **Inverted Index**: Utilizes an inverted index for efficient search and retrieval.
- **Scalability**: Designed to scale horizontally with large volumes of data.

### Setup

1. **Pull Docker Image**: Pull the Weaviate Docker image from the Docker registry.
2. **Configure Docker Compose**: Set the Weaviate image name in the `docker-compose.yml` file located in the `elasticsearch` directory.
3. **Build Docker Image**: Run the following command to build the Docker image:
   ```bash
   docker compose up --build
4. **Access FastAPI UI**: Once the service is running, you can access the FastAPI UI at localhost:9000/docs.

# Locust Performance Testing

The directories contain a Locust performance testing script and performance result designed to evaluate the load and performance of a duplicate detection API. The script simulates user interactions with the API and provides insights into how the system handles varying levels of traffic.

## Scenario

The performance test focuses on the `/search_duplicate` API endpoint, which performs duplicate detection based on given parameters. The test aims to:

- Simulate users sending requests to the API with various payloads.
- Assess the system's response time and capacity under different loads.
- Observe the system's behavior during specified periods of increased traffic.

### Test Scenarios

1. **Duplicate Detection Requests**: Simulates sending requests with both valid and invalid payloads.
2. **Load Shaping**: Uses the `StagesShape` class to control the load by increasing the number of concurrent users and managing the user spawn rate over time.

## Files

- `locustfile.py`: Contains the Locust test script with user scenarios and load shaping configuration for Elasticsearch microservice.
- `locustfile.py`: Contains the Locust test script with user scenarios and load shaping configuration for Weaviate microservice.

## Setup

1. **Running the Test**: To execute the performance test, run the following command
   ```bash
   locust -f locustfile.py 
2. **Prepare the API** Once the service is running, you can access the FastAPI UI at localhost:8089/.
