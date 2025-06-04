#!/bin/bash
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting Pipeline"
echo "----------------------------------------"

echo "Building Docker images..."
docker-compose build

echo "Starting MLflow server..."
docker-compose up -d mlflow
sleep 10

echo "Running ETL Pipeline..."
docker-compose run --rm spark-app python src/etl.py

echo "Running ML Training Pipeline..."
docker-compose run --rm spark-app python src/ml.py

echo "Pipeline executed successfully!"
echo "----------------------------------------"
echo "MLflow UI: http://localhost:5001"
echo "Spark UI: http://localhost:4040"
echo "Data Locations:"
echo "   - Bronze: data/bronze/student_performance"
echo "   - Silver: data/silver/student_performance"
echo "----------------------------------------"

read -p "Stop all services? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose down
    echo "All services stopped."
fi