#!/bin/bash
set -e  # Exit on error


echo "Building Docker image for linux/amd64..."
docker buildx build --platform linux/amd64 -t stock-quantum-project-backend:latest backend/

echo "Tagging image..."
docker tag stock-quantum-project-backend:latest gholder513/stock-quantum-project-backend:latest

echo "Pushing to Docker Hub..."
docker push gholder513/stock-quantum-project-backend:latest 
render deploys create srv-csdtj4btq21c73a8kic0 --wait --confirm