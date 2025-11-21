#!/bin/bash

# Configuration
IMAGE_NAME="usernametron/usernametrondeconstruction.station"
TAG="latest"

echo "🐳 Building Docker image: $IMAGE_NAME:$TAG..."
docker build -t $IMAGE_NAME:$TAG .

echo "🔑 Logging in to Docker Hub..."
echo "Please enter your Docker Hub password if prompted."
docker login

echo "🚀 Pushing image to Docker Hub..."
docker push $IMAGE_NAME:$TAG

echo "✅ Done! Your image is available at $IMAGE_NAME:$TAG"
