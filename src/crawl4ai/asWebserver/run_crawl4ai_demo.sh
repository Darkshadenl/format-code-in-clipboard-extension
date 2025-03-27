#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")"

echo "Starting Crawl4AI container..."
docker compose up -d

# Wait for the container to start
echo "Waiting for Crawl4AI to start (10 seconds)..."
sleep 10

# Check if the container is running
if ! docker ps | grep -q crawl4ai; then
  echo "Error: Crawl4AI container is not running."
  echo "Check the logs with: docker compose logs"
  exit 1
fi

echo "Crawl4AI container is running."

# Navigate to the pyplayground directory
cd pyplayground

# Activate the virtual environment and install dependencies
echo "Setting up Python environment..."
poetry install

# Run the API server in the background
echo "Starting the Crawl4AI Mini API..."
poetry run python -m pyplayground run &
API_PID=$!

# Wait for the API to start
echo "Waiting for the API to start (5 seconds)..."
sleep 5

# Test scraping nu.nl
echo "Testing scraping nu.nl..."
poetry run python -m pyplayground test

# Cleanup
echo "Cleaning up..."
kill $API_PID

# Return to the original directory
cd ..

echo "Demo complete. Results saved to pyplayground/nu_nl_scrape_result.md"
echo "To stop the Crawl4AI container, run: docker compose down" 